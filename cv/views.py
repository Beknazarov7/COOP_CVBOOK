from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import os
import logging
from django.http import FileResponse
import subprocess
import tempfile
from django.template.loader import render_to_string

from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import redirect
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import CVSubmission
logger = logging.getLogger(__name__)

def generate_pdf(cv):
    """
    Generate a PDF from the CV using LaTeX template
    """
    logger.info(f"Generating PDF for CV ID {cv.id} using LaTeX")
    from .models import Education, Certificate, ProfessionalExperience, ProfessionalCompetency, Project, TechnicalSkill, Language, CommunityInvolvement, Award, Reference
    
    # Gather all related data
    educations = cv.educations.all()
    experiences = cv.experiences.all()
    competencies = cv.competencies.all()
    projects = cv.projects.all()
    technical_skills = cv.technical_skills.all()
    languages = cv.languages.all()
    community_involvements = cv.community_involvements.all()
    awards = cv.awards.all()
    references = cv.references.all()

    # Prepare context for template
    context = {
        'cv': cv,
        'educations': educations,
        'experiences': experiences,
        'competencies': competencies,
        'projects': projects,
        'technical_skills': technical_skills,
        'languages': languages,
        'community_involvements': community_involvements,
        'awards': awards,
        'references': references,
    }
    
    # Render LaTeX template
    latex_content = render_to_string('cv.tex', context)
    
    # Create output directory for PDFs
    pdf_output_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
    os.makedirs(pdf_output_dir, exist_ok=True)
    
    # Create temporary directory for LaTeX compilation
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write .tex file
        tex_path = os.path.join(tmpdir, f'cv_{cv.id}.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Compile LaTeX to PDF
        try:
            # Check if pdflatex is available
            check_latex = subprocess.run(
                ['which', 'pdflatex'],
                capture_output=True,
                text=True
            )
            
            if check_latex.returncode != 0:
                error_msg = (
                    "pdflatex is not installed. Please install it using:\n"
                    "sudo apt-get update && sudo apt-get install -y texlive-latex-base texlive-latex-extra texlive-fonts-recommended"
                )
                logger.error(error_msg)
                raise Exception(error_msg)
            
            # Run pdflatex twice to ensure proper rendering of references and page numbers
            for run_number in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', f'cv_{cv.id}.tex'],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Only check for errors on the final run
                # LaTeX often has warnings but still produces a valid PDF
                if run_number == 1:  # Second (final) run
                    temp_pdf_check = os.path.join(tmpdir, f'cv_{cv.id}.pdf')
                    if not os.path.exists(temp_pdf_check):
                        logger.error(f"LaTeX compilation failed - no PDF produced")
                        logger.error(f"LaTeX stderr: {result.stderr}")
                        logger.error(f"LaTeX stdout: {result.stdout}")
                        raise Exception(f"LaTeX compilation failed - no PDF file was generated")
            
            # Move the generated PDF to the media directory
            temp_pdf_path = os.path.join(tmpdir, f'cv_{cv.id}.pdf')
            final_pdf_path = os.path.join(pdf_output_dir, f'cv_{cv.id}.pdf')
            
            if os.path.exists(temp_pdf_path):
                import shutil
                shutil.copy2(temp_pdf_path, final_pdf_path)
                logger.info(f"PDF successfully generated at {final_pdf_path}")
                
                # Return relative path for URL
                relative_path = os.path.relpath(final_pdf_path, settings.MEDIA_ROOT).replace(os.sep, '/')
                return f'/media/{relative_path}'
            else:
                raise Exception("PDF file was not generated")
                
        except subprocess.TimeoutExpired:
            logger.error("LaTeX compilation timed out")
            raise Exception("PDF generation timed out")
        except Exception as e:
            logger.error(f"Failed to generate PDF for cv_id {cv.id}: {str(e)}")
            raise

class CVSubmitView(APIView):
    parser_classes = [JSONParser]
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            logger.info("CVSubmitView.post called with data: %s", request.data)
            data = request.data
            # --------- Normalize client payload keys for backward/variant names ----------
            def normalize_education_item(edu):
                # Map British spelling and alternate field names
                if 'honours' in edu and not edu.get('honors'):
                    edu['honors'] = edu.get('honours')
                if 'courses' in edu and not edu.get('relevant_courses'):
                    edu['relevant_courses'] = edu.get('courses')
                return edu

            def normalize_experience_item(exp):
                # Combine start/end dates into single 'dates' string if provided
                start = (exp.get('start_date') or '').strip()
                end = (exp.get('end_date') or '').strip()
                if (start or end) and not exp.get('dates'):
                    exp['dates'] = f"{start} – {end or 'Present'}".strip(' –')
                return exp

            def normalize_technical_skills(ts):
                # Accept new grouped keys and map them to model fields
                mapped = {
                    'programming_languages': ts.get('programming_languages') or ts.get('programming_stat_tools') or '',
                    'frameworks_databases': ts.get('frameworks_databases') or '',
                    'tools': ts.get('tools') or ts.get('data_analysis_viz') or '',
                    'web_development': ts.get('web_development') or ts.get('web_software_dev') or '',
                    'multimedia': ts.get('multimedia') or ts.get('media_design_tools') or '',
                    'network': ts.get('network') or ts.get('communication_collaboration') or '',
                    'operating_systems': ts.get('operating_systems') or '',
                }
                return mapped
            # --------- Deduplicate incoming repeated list entries (defensive) ----------
            def dedup_list(items, key_fields):
                seen = set()
                unique = []
                for item in items or []:
                    # Build a safe fingerprint using stringified values
                    key = tuple((k, str(item.get(k) or "").strip()) for k in key_fields)
                    # Only dedup when there is at least one non-empty key to identify the item
                    if any(v for (_, v) in key):
                        if key in seen:
                            continue
                        seen.add(key)
                    unique.append(item)
                return unique

            name = data.get('name')
            surname = data.get('surname')
            email = data.get('email')
            major = data.get('major', '')
            country = data.get('country', '')
            city = data.get('city', '')
            phone = data.get('phone', '')
            linkedin = data.get('linkedin', '')
            github = data.get('github', '')
            graduation_year = data.get('graduationYear', '')
            status_preference = data.get('status', '')
            
            # Student-specific fields
            user_type = data.get('user_type', '')
            cohort_status = data.get('cohort_status', '')
            is_uca_student = user_type == 'student'
            
            if not all([name, surname, email]):
                logger.error("Missing required fields: name, surname, or email")
                return Response({"error": "name, surname, and email are required"}, status=status.HTTP_400_BAD_REQUEST)

            from .models import CVSubmission
            
            # Determine if CV should be auto-published to CVBook (only for Senior students)
            auto_publish = is_uca_student and cohort_status == 'Senior'
            
            cv, created = CVSubmission.objects.get_or_create(
                email=email, 
                defaults={
                    'name': name, 
                    'surname': surname, 
                    'major': major,
                    'country': country,
                    'city': city,
                    'phone': phone,
                    'linkedin': linkedin,
                    'github': github,
                    'graduation_year': graduation_year,
                    'status_preference': status_preference,
                    'is_uca_student': is_uca_student,
                    'cohort_status': cohort_status,
                    'is_published_to_cvbook': auto_publish,
                    'admin_approved': auto_publish  # Auto-approve senior students
                }
            )
            if not created:
                cv.name = name
                cv.surname = surname
                cv.major = major
                cv.country = country
                cv.city = city
                cv.phone = phone
                cv.linkedin = linkedin
                cv.github = github
                cv.graduation_year = graduation_year
                cv.status_preference = status_preference
                cv.is_uca_student = is_uca_student
                cv.cohort_status = cohort_status
                
                # Update publication status if it's a senior student
                if is_uca_student and cohort_status == 'Senior':
                    cv.is_published_to_cvbook = True
                    cv.admin_approved = True
                
                cv.save()
                cv.educations.all().delete()
                cv.experiences.all().delete()
                cv.competencies.all().delete()
                cv.projects.all().delete()
                cv.technical_skills.all().delete()
                cv.languages.all().delete()
                cv.community_involvements.all().delete()
                cv.awards.all().delete()
                cv.references.all().delete()

            from .models import Education, Certificate, ProfessionalExperience, ProfessionalCompetency, Project, TechnicalSkill, Language, CommunityInvolvement, Award, Reference
            # Apply de-duplication on lists
            educations_in_raw = [normalize_education_item(e or {}) for e in data.get('educations', [])]
            educations_in = dedup_list(educations_in_raw, ['degree_title', 'university', 'start_date', 'expected_graduation', 'university_location', 'gpa', 'honors', 'relevant_courses'])
            experiences_in_raw = [normalize_experience_item(e or {}) for e in data.get('experiences', [])]
            experiences_in = dedup_list(experiences_in_raw, ['position_title', 'company', 'location', 'employment_type', 'dates', 'accomplishments'])
            competencies_in = dedup_list(data.get('competencies', []), ['competency_type', 'key_accomplishments'])
            projects_in = dedup_list(data.get('projects', []), ['project_title', 'year', 'technologies_used', 'summary', 'accomplishment'])
            languages_in = dedup_list(data.get('languages', []), ['name', 'proficiency'])
            # Normalize community involvement dates similar to experiences
            def normalize_comm_item(ci):
                s = (ci.get('start_date') or '').strip()
                e = (ci.get('end_date') or '').strip()
                if (s or e) and not ci.get('dates'):
                    ci['dates'] = f"{s} – {e or 'Present'}".strip(' –')
                return ci
            community_involvements_in_raw = [normalize_comm_item(ci or {}) for ci in data.get('community_involvements', [])]
            community_involvements_in = dedup_list(community_involvements_in_raw, ['organization', 'position_title', 'location', 'dates', 'achievements'])
            awards_in = dedup_list(data.get('awards', []), ['award_name', 'year', 'presenting_organization', 'short_description'])
            references_in = dedup_list(data.get('references', []), ['reference_name', 'email', 'phone', 'position', 'company'])

            for edu_data in educations_in:
                # Skip empty education entries
                if not edu_data.get('degree_title') and not edu_data.get('university'):
                    logger.info("Skipping empty education entry: %s", edu_data)
                    continue
                    
                required_fields = ['degree_title', 'university']
                if not all(edu_data.get(k) for k in required_fields):
                    logger.warning("Incomplete education data (missing degree_title or university): %s", edu_data)
                    # Continue anyway with what we have
                    if not edu_data.get('degree_title'):
                        edu_data['degree_title'] = 'Degree'
                    if not edu_data.get('university'):
                        edu_data['university'] = 'University'
                
                # Filter only valid Education fields
                valid_edu_fields = {k: v for k, v in edu_data.items() if k in ['degree_title', 'university', 'start_date', 'expected_graduation', 'university_location', 'honors', 'relevant_courses', 'gpa']}
                education = Education.objects.create(cv=cv, **valid_edu_fields)
                
                for cert_data in dedup_list(edu_data.get('certificates', []), ['certificate_title', 'organization', 'year', 'location']):
                    if not cert_data.get('certificate_title'):
                        logger.info("Skipping certificate with no title: %s", cert_data)
                        continue
                    
                    # Filter only valid Certificate fields
                    valid_cert_fields = {k: v for k, v in cert_data.items() if k in ['certificate_title', 'organization', 'year', 'location']}
                    try:
                        Certificate.objects.create(education=education, **valid_cert_fields)
                    except Exception as e:
                        logger.error("Error creating certificate: %s. Data: %s - Skipping this certificate", str(e), cert_data)
                        # Don't fail the entire submission, just skip this certificate
                        continue

            for exp_data in experiences_in:
                # Skip empty experience entries
                if not exp_data.get('position_title') and not exp_data.get('company'):
                    logger.info("Skipping empty experience entry: %s", exp_data)
                    continue
                    
                required_fields = ['position_title', 'company']
                if not all(exp_data.get(k) for k in required_fields):
                    logger.warning("Incomplete experience data: %s", exp_data)
                    # Continue anyway with what we have
                    if not exp_data.get('position_title'):
                        exp_data['position_title'] = 'Position'
                    if not exp_data.get('company'):
                        exp_data['company'] = 'Company'
                
                # Filter only valid ProfessionalExperience fields
                valid_exp_fields = {k: v for k, v in exp_data.items() if k in ['position_title', 'company', 'location', 'employment_type', 'start_date', 'end_date', 'dates', 'accomplishments']}
                ProfessionalExperience.objects.create(cv=cv, **valid_exp_fields)

            for comp_data in competencies_in:
                if not comp_data.get('competency_type') and not comp_data.get('key_accomplishments'):
                    logger.info("Skipping competency as both competency_type and key_accomplishments are empty: %s", comp_data)
                    continue
                if not comp_data.get('competency_type'):
                    logger.warning("Competency missing type, using default: %s", comp_data)
                    comp_data['competency_type'] = 'Competency'
                
                # Filter only valid ProfessionalCompetency fields
                valid_comp_fields = {k: v for k, v in comp_data.items() if k in ['competency_type', 'key_accomplishments']}
                ProfessionalCompetency.objects.create(cv=cv, **valid_comp_fields)

            for proj_data in projects_in:
                if not proj_data.get('project_title'):
                    logger.info("Skipping project with no title: %s", proj_data)
                    continue
                
                # Filter only valid Project fields
                valid_proj_fields = {k: v for k, v in proj_data.items() if k in ['project_title', 'year', 'technologies_used', 'summary', 'accomplishment']}
                Project.objects.create(cv=cv, **valid_proj_fields)

            if 'technical_skills' in data:
                tech_skills = normalize_technical_skills(data['technical_skills'] or {})
                # Filter only valid TechnicalSkill fields
                valid_tech_fields = {k: v for k, v in tech_skills.items() if k in [
                    'programming_languages', 'frameworks_databases', 'tools', 
                    'web_development', 'multimedia', 'network', 'operating_systems'
                ]}
                
                if any(valid_tech_fields.values()):
                    TechnicalSkill.objects.update_or_create(cv=cv, defaults=valid_tech_fields)
                else:
                    logger.info("Skipping technical skills as all fields are empty")
                    cv.technical_skills.all().delete()

            for lang_data in languages_in:
                if not lang_data.get('name'):
                    logger.info("Skipping language as name is empty: %s", lang_data)
                    continue
                
                # Filter only valid Language fields
                valid_lang_fields = {k: v for k, v in lang_data.items() if k in ['name', 'proficiency']}
                Language.objects.create(cv=cv, **valid_lang_fields)

            for comm_data in community_involvements_in:
                # Skip if all fields are empty
                if not any([comm_data.get(k) for k in ['organization', 'position_title', 'dates', 'achievements', 'location']]):
                    logger.info("Skipping empty community involvement: %s", comm_data)
                    continue
                
                valid_fields = {k: v for k, v in comm_data.items() if k in ['organization', 'position_title', 'location', 'start_date', 'end_date', 'dates', 'achievements']}
                CommunityInvolvement.objects.create(cv=cv, **valid_fields)

            for award_data in awards_in:
                # Skip if no award name
                if not award_data.get('award_name'):
                    logger.info("Skipping award with no name: %s", award_data)
                    continue
                
                valid_fields = {k: v for k, v in award_data.items() if k in ['award_name', 'year', 'presenting_organization', 'short_description']}
                Award.objects.create(cv=cv, **valid_fields)

            for ref_data in references_in:
                if not all([ref_data.get(k) for k in ['reference_name', 'email']]):
                    logger.info("Skipping reference with missing required fields: %s", ref_data)
                    continue
                
                # Filter only valid Reference fields
                valid_ref_fields = {k: v for k, v in ref_data.items() if k in ['reference_name', 'position', 'company', 'email', 'phone', 'relation']}
                Reference.objects.create(cv=cv, **valid_ref_fields)

            logger.info("Generating PDF for cv_id: %s", cv.id)
            pdf_path = generate_pdf(cv)
            logger.info("PDF generated at: %s", pdf_path)

            return Response({
                "message": f"CV {'created' if created else 'updated'} successfully",
                "cv_id": cv.id,
                "pdf_url": pdf_path,
                "submitted_at": cv.submitted_at.isoformat(),
                "success": True
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Unexpected error in CVSubmitView: {str(e)}", exc_info=True)
            return Response({
                "error": f"An unexpected error occurred: {str(e)}",
                "success": False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CVPDFView(APIView):
    def get(self, request, cv_id):
        logger.info("CVPDFView.get called for cv_id: %s", cv_id)
        from .models import CVSubmission
        try:
            cv = CVSubmission.objects.get(id=cv_id)
            pdf_output_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
            pdf_path = os.path.join(pdf_output_dir, f'cv_{cv.id}.pdf')
            if not os.path.exists(pdf_path):
                logger.error("PDF not found for cv_id: %s", cv_id)
                return Response({"error": "PDF not generated yet"}, status=status.HTTP_404_NOT_FOUND)
            return FileResponse(open(pdf_path, 'rb'), as_attachment=True, filename=f'cv_{cv.name}_{cv.surname}.pdf')
        except CVSubmission.DoesNotExist:
            logger.error("CV not found for cv_id: %s", cv_id)
            return Response({"error": "CV not found"}, status=status.HTTP_404_NOT_FOUND)

class CVEditView(APIView):
    parser_classes = [JSONParser]

    def get(self, request, cv_id):
        logger.info("CVEditView.get called for cv_id: %s", cv_id)
        from .models import CVSubmission, Education, Certificate, ProfessionalExperience, ProfessionalCompetency, Project, TechnicalSkill, Language, CommunityInvolvement, Award, Reference
        try:
            cv = CVSubmission.objects.get(id=cv_id)
            data = {
                "name": cv.name,
                "surname": cv.surname,
                "email": cv.email,
                "major": cv.major,
                "country": cv.country,
                "graduation_year": cv.graduation_year,
                "status_preference": cv.status_preference,
                "educations": [
                    {
                        "id": edu.id,
                        "degree_title": edu.degree_title,
                        "university": edu.university,
                        "start_date": edu.start_date,
                        "expected_graduation": edu.expected_graduation,
                        "university_location": edu.university_location,
                        "certificates": [
                            {
                                "id": cert.id,
                                "certificate_title": cert.certificate_title,
                                "organization": cert.organization,
                                "year": cert.year
                            } for cert in edu.certificates.all()
                        ]
                    } for edu in cv.educations.all()
                ],
                "experiences": [
                    {
                        "id": exp.id,
                        "position_title": exp.position_title,
                        "company": exp.company,
                        "dates": exp.dates,
                        "accomplishments": exp.accomplishments
                    } for exp in cv.experiences.all()
                ],
                "competencies": [
                    {
                        "id": comp.id,
                        "competency_type": comp.competency_type,
                        "key_accomplishments": comp.key_accomplishments
                    } for comp in cv.competencies.all()
                ],
                "projects": [
                    {
                        "id": proj.id,
                        "project_title": proj.project_title,
                        "year": proj.year,
                        "summary": proj.summary
                    } for proj in cv.projects.all()
                ],
                "technical_skills": {
                    "id": technical_skills.id if (technical_skills := cv.technical_skills.first()) else None,
                    "programming_languages": technical_skills.programming_languages if technical_skills else "",
                    "frameworks_databases": technical_skills.frameworks_databases if technical_skills else "",
                    "tools": technical_skills.tools if technical_skills else ""
                },
                "languages": [
                    {"id": lang.id, "name": lang.name} for lang in cv.languages.all()
                ],
                "community_involvements": [
                    {
                        "id": ci.id,
                        "position_title": ci.position_title,
                        "organization": ci.organization,
                        "dates": ci.dates,
                        "achievements": ci.achievements
                    } for ci in cv.community_involvements.all()
                ],
                "awards": [
                    {
                        "id": award.id,
                        "award_name": award.award_name,
                        "year": award.year,
                        "short_description": award.short_description
                    } for award in cv.awards.all()
                ],
                "references": [
                    {
                        "id": ref.id,
                        "reference_name": ref.reference_name,
                        "position": ref.position,
                        "email": ref.email,
                        "phone": ref.phone
                    } for ref in cv.references.all()
                ]
            }
            logger.info("CV details retrieved for editing cv_id: %s", cv_id)
            return Response(data, status=status.HTTP_200_OK)
        except CVSubmission.DoesNotExist:
            logger.error("CV not found for cv_id: %s", cv_id)
            return Response({"error": "CV not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, cv_id):
        logger.info("CVEditView.put called for cv_id: %s with data: %s", cv_id, request.data)
        from .models import CVSubmission, Education, Certificate, ProfessionalExperience, ProfessionalCompetency, Project, TechnicalSkill, Language, CommunityInvolvement, Award, Reference
        try:
            cv = CVSubmission.objects.get(id=cv_id)
            data = request.data
            cv.name = data.get('name', cv.name)
            cv.surname = data.get('surname', cv.surname)
            cv.email = data.get('email', cv.email)
            cv.major = data.get('major', cv.major)
            cv.country = data.get('country', cv.country)
            cv.graduation_year = data.get('graduation_year', cv.graduation_year)
            cv.status_preference = data.get('status_preference', cv.status_preference)
            cv.save()

            for edu_data in data.get('educations', []):
                edu_id = edu_data.get('id')
                if edu_id:
                    education = Education.objects.get(id=edu_id, cv=cv)
                    for key, value in edu_data.items():
                        if key != 'id' and key != 'certificates':
                            setattr(education, key, value)
                    education.save()
                    education.certificates.all().delete()
                    for cert_data in edu_data.get('certificates', []):
                        cert_id = cert_data.get('id')
                        if cert_id:
                            cert = Certificate.objects.get(id=cert_id, education=education)
                            for key, value in cert_data.items():
                                if key != 'id':
                                    setattr(cert, key, value)
                            cert.save()
                        else:
                            Certificate.objects.create(education=education, **{k: v for k, v in cert_data.items() if k != 'id'})
                else:
                    education = Education.objects.create(cv=cv, **{k: v for k, v in edu_data.items() if k != 'id' and k != 'certificates'})
                    for cert_data in edu_data.get('certificates', []):
                        Certificate.objects.create(education=education, **{k: v for k, v in cert_data.items() if k != 'id'})

            for exp_data in data.get('experiences', []):
                exp_id = exp_data.get('id')
                if exp_id:
                    exp = ProfessionalExperience.objects.get(id=exp_id, cv=cv)
                    for key, value in exp_data.items():
                        if key != 'id':
                            setattr(exp, key, value)
                    exp.save()
                else:
                    ProfessionalExperience.objects.create(cv=cv, **{k: v for k, v in exp_data.items() if k != 'id'})

            for comp_data in data.get('competencies', []):
                comp_id = comp_data.get('id')
                if comp_id:
                    comp = ProfessionalCompetency.objects.get(id=comp_id, cv=cv)
                    for key, value in comp_data.items():
                        if key != 'id':
                            setattr(comp, key, value)
                    comp.save()
                else:
                    ProfessionalCompetency.objects.create(cv=cv, **{k: v for k, v in comp_data.items() if k != 'id'})

            for proj_data in data.get('projects', []):
                proj_id = proj_data.get('id')
                if proj_id:
                    proj = Project.objects.get(id=proj_id, cv=cv)
                    for key, value in proj_data.items():
                        if key != 'id':
                            setattr(proj, key, value)
                    proj.save()
                else:
                    Project.objects.create(cv=cv, **{k: v for k, v in proj_data.items() if k != 'id'})

            if 'technical_skills' in data:
                tech_data = data['technical_skills']
                tech_id = tech_data.get('id')
                if tech_id:
                    tech = TechnicalSkill.objects.get(id=tech_id, cv=cv)
                    for key, value in tech_data.items():
                        if key != 'id':
                            setattr(tech, key, value)
                    tech.save()
                else:
                    TechnicalSkill.objects.update_or_create(cv=cv, defaults=tech_data)

            for lang_data in data.get('languages', []):
                lang_id = lang_data.get('id')
                if lang_id:
                    lang = Language.objects.get(id=lang_id, cv=cv)
                    for key, value in lang_data.items():
                        if key != 'id':
                            setattr(lang, key, value)
                    lang.save()
                else:
                    Language.objects.create(cv=cv, **{k: v for k, v in lang_data.items() if k != 'id'})

            for comm_data in data.get('community_involvements', []):
                comm_id = comm_data.get('id')
                if comm_id:
                    comm = CommunityInvolvement.objects.get(id=comm_id, cv=cv)
                    for key, value in comm_data.items():
                        if key != 'id':
                            setattr(comm, key, value)
                    comm.save()
                else:
                    CommunityInvolvement.objects.create(cv=cv, **{k: v for k, v in comm_data.items() if k != 'id'})

            for award_data in data.get('awards', []):
                award_id = award_data.get('id')
                if award_id:
                    award = Award.objects.get(id=award_id, cv=cv)
                    for key, value in award_data.items():
                        if key != 'id':
                            setattr(award, key, value)
                    award.save()
                else:
                    Award.objects.create(cv=cv, **{k: v for k, v in award_data.items() if k != 'id'})

            for ref_data in data.get('references', []):
                ref_id = ref_data.get('id')
                if ref_id:
                    ref = Reference.objects.get(id=ref_id, cv=cv)
                    for key, value in ref_data.items():
                        if key != 'id':
                            setattr(ref, key, value)
                    ref.save()
                else:
                    Reference.objects.create(cv=cv, **{k: v for k, v in ref_data.items() if k != 'id'})

            logger.info("Regenerating PDF for cv_id: %s", cv.id)
            pdf_path = generate_pdf(cv)
            logger.info("PDF regenerated at: %s", pdf_path)

            return Response({"message": "CV updated", "cv_id": cv.id, "pdf_url": pdf_path}, status=status.HTTP_200_OK)
        except CVSubmission.DoesNotExist:
            logger.error("CV not found for cv_id: %s", cv_id)
            return Response({"error": "CV not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error("Error updating CV %s: %s", cv_id, str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CVDetailView(APIView):
    def get(self, request, cv_id):
        logger.info("CVDetailView.get called for cv_id: %s", cv_id)
        from .models import CVSubmission, Education, Certificate, ProfessionalExperience, ProfessionalCompetency, Project, TechnicalSkill, Language, CommunityInvolvement, Award, Reference
        try:
            cv = CVSubmission.objects.get(id=cv_id)
            technical_skills = cv.technical_skills.first()
            data = {
                "name": cv.name,
                "surname": cv.surname,
                "email": cv.email,
                "major": cv.major,
                "country": cv.country,
                "graduation_year": cv.graduation_year,
                "status_preference": cv.status_preference,
                "submitted_at": cv.submitted_at.isoformat(),
                "educations": [
                    {
                        "degree_title": edu.degree_title,
                        "university": edu.university,
                        "start_date": edu.start_date,
                        "expected_graduation": edu.expected_graduation,
                        "university_location": edu.university_location,
                        "certificates": [
                            {
                                "certificate_title": cert.certificate_title,
                                "organization": cert.organization,
                                "year": cert.year
                            } for cert in edu.certificates.all()
                        ]
                    } for edu in cv.educations.all()
                ],
                "experiences": [
                    {
                        "position_title": exp.position_title,
                        "company": exp.company,
                        "dates": exp.dates,
                        "accomplishments": exp.accomplishments
                    } for exp in cv.experiences.all()
                ],
                "competencies": [
                    {
                        "competency_type": comp.competency_type,
                        "key_accomplishments": comp.key_accomplishments
                    } for comp in cv.competencies.all()
                ],
                "projects": [
                    {
                        "project_title": proj.project_title,
                        "year": proj.year,
                        "summary": proj.summary
                    } for proj in cv.projects.all()
                ],
                "technical_skills": {
                    "programming_languages": technical_skills.programming_languages if technical_skills else "",
                    "frameworks_databases": technical_skills.frameworks_databases if technical_skills else "",
                    "tools": technical_skills.tools if technical_skills else ""
                },
                "languages": [{"name": lang.name} for lang in cv.languages.all()],
                "community_involvements": [
                    {
                        "position_title": ci.position_title,
                        "organization": ci.organization,
                        "dates": ci.dates,
                        "achievements": ci.achievements
                    } for ci in cv.community_involvements.all()
                ],
                "awards": [
                    {
                        "award_name": award.award_name,
                        "year": award.year,
                        "short_description": award.short_description
                    } for award in cv.awards.all()
                ],
                "references": [
                    {
                        "reference_name": ref.reference_name,
                        "position": ref.position,
                        "email": ref.email,
                        "phone": ref.phone
                    } for ref in cv.references.all()
                ]
            }
            logger.info("CV details retrieved for cv_id: %s", cv_id)
            return Response(data, status=status.HTTP_200_OK)
        except CVSubmission.DoesNotExist:
            logger.error("CV not found for cv_id: %s", cv_id)
            return Response({"error": "CV not found"}, status=status.HTTP_404_NOT_FOUND)

class CVListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logger.info("CVListView.get called")
        from .models import CVSubmission
        
        # Check if this is a request for student's own CVs
        student_email = request.GET.get('student_email')
        management_request = request.GET.get('management', '').lower() == 'true'
        
        if student_email:
            # Return all CVs for this specific student
            cvs = CVSubmission.objects.filter(email=student_email).prefetch_related('technical_skills', 'languages')
        elif management_request:
            # Return ALL CVs for management system
            cvs = CVSubmission.objects.all().prefetch_related('technical_skills', 'languages').order_by('-submitted_at')
        else:
            # Return only published CVs for public CVBook display
            cvs = CVSubmission.objects.filter(
                is_published_to_cvbook=True,
                admin_approved=True
            ).prefetch_related('technical_skills', 'languages')
        serialized_data = [
            {
                'id': cv.id,
                'name': cv.name,
                'surname': cv.surname,
                'email': cv.email,
                'major': cv.major,
                'country': cv.country,
                'graduation_year': cv.graduation_year,
                'status_preference': cv.status_preference,
                'submitted_at': cv.submitted_at.isoformat(),
                'is_uca_student': cv.is_uca_student,
                'cohort_status': cv.cohort_status,
                'admin_approved': cv.admin_approved,
                'is_published_to_cvbook': cv.is_published_to_cvbook,
                'technical_skills': [
                    {
                        'programming_languages': ts.programming_languages,
                        'frameworks_databases': ts.frameworks_databases,
                        'tools': ts.tools,
                        'web_development': ts.web_development,
                        'multimedia': ts.multimedia,
                        'network': ts.network,
                        'operating_systems': ts.operating_systems
                    }
                    for ts in cv.technical_skills.all()
                ] if cv.technical_skills.exists() else [],
                'languages': [{'name': lang.name} for lang in cv.languages.all()] if cv.languages.exists() else []
            }
            for cv in cvs
        ]
        return Response(serialized_data, status=status.HTTP_200_OK)

def cv_detail_view(request, cv_id):
    from .models import CVSubmission, Education, Certificate, ProfessionalExperience, ProfessionalCompetency, Project, TechnicalSkill, Language, CommunityInvolvement, Award, Reference
    try:
        cv = CVSubmission.objects.get(id=cv_id)
        context = {
            'cv': cv,
            'educations': cv.educations.all(),
            'experiences': cv.experiences.all(),
            'competencies': cv.competencies.all(),
            'projects': cv.projects.all(),
            'technical_skills': cv.technical_skills.all(),
            'languages': cv.languages.all(),
            'community_involvements': cv.community_involvements.all(),
            'awards': cv.awards.all(),
            'references': cv.references.all(),
        }
        return render(request, 'cv/cv-detail.html', context)
    except CVSubmission.DoesNotExist:
        return render(request, 'cv/cv-cards.html', {'cvs': CVSubmission.objects.all().order_by('-submitted_at'), 'error': 'CV not found'})
    
def cv_cards_view(request):
    """
    Public CV cards view - shows published and approved CVs
    """
    cvs = CVSubmission.objects.filter(
        is_published_to_cvbook=True,
        admin_approved=True
    ).order_by('-submitted_at')
    
    return render(request, 'cv/cv-cards.html', {'cvs': cvs})

from rest_framework import serializers
from .models import CVSubmission

class CVSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVSubmission
        fields = '__all__'

def admin_cv_cards_view(request):
    """
    Special view for admin users to access CVBook without separate authentication
    """
    # Check if request has admin token or is from admin panel
    admin_token = request.GET.get('admin_token')

    if admin_token == 'ucacoop_admin_access_2025':  # Simple token for admin access
        # Render the CVBook page directly without authentication
        cvs = CVSubmission.objects.filter(
            is_published_to_cvbook=True,
            admin_approved=True
        ).order_by('-submitted_at')

        return render(request, 'cv/cv-cards.html', {'cvs': cvs, 'admin_access': True})

    # If no valid admin token, redirect to regular cv-cards which requires auth
    return redirect('/#cv-cards')

@api_view(['POST'])
@permission_classes([AllowAny])
def cv_management_action(request):
    """
    Handle CV management actions from admin panel
    """
    try:
        action = request.data.get('action')
        cv_id = request.data.get('cv_id')
        
        if not cv_id or not action:
            return Response({'success': False, 'message': 'Missing required parameters'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        cv = CVSubmission.objects.get(id=cv_id)
        
        # Handle 'publish' or 'toggle_publish'
        if action in ['publish', 'toggle_publish']:
            if action == 'publish':
                cv.is_published_to_cvbook = True
            else:
                cv.is_published_to_cvbook = not cv.is_published_to_cvbook
            cv.save()
            status_text = 'published' if cv.is_published_to_cvbook else 'unpublished'
            return Response({'success': True, 'message': f'CV {status_text} successfully'})
        
        # Handle 'unpublish'
        elif action == 'unpublish':
            cv.is_published_to_cvbook = False
            cv.save()
            return Response({'success': True, 'message': 'CV unpublished successfully'})
            
        # Handle 'approve' or 'toggle_approve'
        elif action in ['approve', 'toggle_approve']:
            if action == 'approve':
                cv.admin_approved = True
            else:
                cv.admin_approved = not cv.admin_approved
            cv.save()
            status_text = 'approved' if cv.admin_approved else 'unapproved'
            return Response({'success': True, 'message': f'CV {status_text} successfully'})
        
        # Handle 'unapprove'
        elif action == 'unapprove':
            cv.admin_approved = False
            cv.save()
            return Response({'success': True, 'message': 'CV approval removed successfully'})
            
        # Handle 'delete'
        elif action == 'delete':
            cv.delete()
            return Response({'success': True, 'message': 'CV deleted successfully'})
            
        else:
            return Response({'success': False, 'message': f'Invalid action: {action}. Valid actions are: publish, unpublish, approve, unapprove, delete'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
    except CVSubmission.DoesNotExist:
        return Response({'success': False, 'message': 'CV not found'}, 
                      status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error in cv_management_action: {str(e)}")
        return Response({'success': False, 'message': str(e)}, 
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)