#!/usr/bin/env python3
"""
Script to remove duplicate CV entries from the database.
This removes duplicate experiences, projects, awards, references, and community involvements.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CVBOOK.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from cv.models import (
    CVSubmission, ProfessionalExperience, Project, 
    Award, Reference, CommunityInvolvement, Language, ProfessionalCompetency
)
from collections import defaultdict

def remove_duplicates():
    """Remove duplicate entries from CV submissions"""
    
    print("=" * 70)
    print("CV DATABASE DUPLICATE CLEANUP")
    print("=" * 70)
    
    all_cvs = CVSubmission.objects.all()
    print(f"\nProcessing {all_cvs.count()} CV submissions...\n")
    
    total_removed = 0
    
    for cv in all_cvs:
        print(f"Checking CV ID {cv.id}: {cv.name} {cv.surname} ({cv.email})")
        removed_count = 0
        
        # Remove duplicate experiences
        experiences = list(cv.experiences.all())
        seen_exp = set()
        for exp in experiences:
            key = (exp.position_title, exp.company, exp.dates)
            if key in seen_exp:
                print(f"  ✗ Removing duplicate experience: {exp.position_title} at {exp.company}")
                exp.delete()
                removed_count += 1
            else:
                seen_exp.add(key)
        
        # Remove duplicate projects
        projects = list(cv.projects.all())
        seen_proj = set()
        for proj in projects:
            key = (proj.project_title, proj.year)
            if key in seen_proj:
                print(f"  ✗ Removing duplicate project: {proj.project_title} ({proj.year})")
                proj.delete()
                removed_count += 1
            else:
                seen_proj.add(key)
        
        # Remove duplicate awards
        awards = list(cv.awards.all())
        seen_award = set()
        for award in awards:
            key = (award.award_name, award.year)
            if key in seen_award:
                print(f"  ✗ Removing duplicate award: {award.award_name} ({award.year})")
                award.delete()
                removed_count += 1
            else:
                seen_award.add(key)
        
        # Remove duplicate references
        references = list(cv.references.all())
        seen_ref = set()
        for ref in references:
            key = (ref.reference_name, ref.email, ref.phone)
            if key in seen_ref:
                print(f"  ✗ Removing duplicate reference: {ref.reference_name}")
                ref.delete()
                removed_count += 1
            else:
                seen_ref.add(key)
        
        # Remove duplicate community involvements
        comms = list(cv.community_involvements.all())
        seen_comm = set()
        for comm in comms:
            key = (comm.position_title, comm.organization, comm.dates)
            if key in seen_comm:
                print(f"  ✗ Removing duplicate community involvement: {comm.position_title} at {comm.organization}")
                comm.delete()
                removed_count += 1
            else:
                seen_comm.add(key)
        
        # Remove duplicate languages
        languages = list(cv.languages.all())
        seen_lang = set()
        for lang in languages:
            key = lang.name
            if key in seen_lang:
                print(f"  ✗ Removing duplicate language: {lang.name}")
                lang.delete()
                removed_count += 1
            else:
                seen_lang.add(key)
        
        # Remove duplicate competencies
        competencies = list(cv.competencies.all())
        seen_comp = set()
        for comp in competencies:
            key = comp.competency_type
            if key in seen_comp:
                print(f"  ✗ Removing duplicate competency: {comp.competency_type}")
                comp.delete()
                removed_count += 1
            else:
                seen_comp.add(key)
        
        if removed_count == 0:
            print(f"  ✓ No duplicates found")
        else:
            print(f"  ✓ Removed {removed_count} duplicate entries")
            total_removed += removed_count
        
        print()
    
    print("=" * 70)
    print(f"CLEANUP COMPLETE: Removed {total_removed} duplicate entries total")
    print("=" * 70)

if __name__ == "__main__":
    try:
        remove_duplicates()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)















