"""
Database seeding script for development and testing.

Creates sample users, sites, audits, questionnaires, and episodes.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import AsyncSessionLocal
from app.models.user import User, Site, UserRole
from app.models.audit import Audit, Questionnaire, Question, QuestionType, AuditStatus, AuditEpisode
from app.core.security import get_password_hash
from datetime import datetime, timedelta
import uuid


async def create_sites(db: AsyncSession) -> list[Site]:
    """Create sample NHS sites."""
    sites = [
        Site(
            id=str(uuid.uuid4()),
            name="Royal London Hospital",
            code="RLH",
            organization_type="acute",
            address="Whitechapel Road, London E1 1BB",
        ),
        Site(
            id=str(uuid.uuid4()),
            name="St Thomas' Hospital",
            code="STH",
            organization_type="acute",
            address="Westminster Bridge Road, London SE1 7EH",
        ),
        Site(
            id=str(uuid.uuid4()),
            name="Cambridge University Hospitals",
            code="CUH",
            organization_type="academic",
            address="Hills Road, Cambridge CB2 0QQ",
        ),
    ]
    
    for site in sites:
        db.add(site)
    await db.commit()
    
    print(f"✅ Created {len(sites)} sites")
    return sites


async def create_users(db: AsyncSession, sites: list[Site]) -> list[User]:
    """Create sample users with different roles."""
    
    # Simple passwords for development
    passwords = {
        UserRole.ADMIN: "admin",
        UserRole.CLINICIAN: "clinician",
        UserRole.AUDIT_LEAD: "lead",
        UserRole.QI_TEAM: "qi",
    }
    
    users = [
        User(
            id=str(uuid.uuid4()),
            email="admin@example.com",
            hashed_password=get_password_hash(passwords[UserRole.ADMIN]),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
        ),
        User(
            id=str(uuid.uuid4()),
            email="clinician@example.com",
            hashed_password=get_password_hash(passwords[UserRole.CLINICIAN]),
            full_name="Dr. Sarah Johnson",
            role=UserRole.CLINICIAN,
            is_active=True,
            is_verified=True,
        ),
        User(
            id=str(uuid.uuid4()),
            email="audit.lead@example.com",
            hashed_password=get_password_hash(passwords[UserRole.AUDIT_LEAD]),
            full_name="Dr. James Chen",
            role=UserRole.AUDIT_LEAD,
            is_active=True,
            is_verified=True,
        ),
        User(
            id=str(uuid.uuid4()),
            email="qi.team@example.com",
            hashed_password=get_password_hash(passwords[UserRole.QI_TEAM]),
            full_name="Emma Wilson",
            role=UserRole.QI_TEAM,
            is_active=True,
            is_verified=True,
        ),
    ]
    
    # Assign users to sites
    for user in users[1:]:  # Skip admin
        user.sites.append(sites[0])
    
    for user in users:
        db.add(user)
    await db.commit()
    
    print(f"✅ Created {len(users)} users")
    print("   Login credentials:")
    for user in users:
        password = passwords.get(user.role, "password")
        print(f"   - {user.email} / {password} ({user.role.value})")
    
    return users


async def create_questionnaires(db: AsyncSession, audit_lead: User, sites: list[Site]) -> list[Questionnaire]:
    """Create sample questionnaires."""
    
    # Hip Fracture Audit Questionnaire
    hip_fracture_q = Questionnaire(
        id=str(uuid.uuid4()),
        title="Hip Fracture Care Pathway",
        description="National Hip Fracture Database (NHFD) style audit",
        version=1,
        created_by_id=audit_lead.id,
        site_id=sites[0].id,
        is_published=True,
    )
    db.add(hip_fracture_q)
    await db.flush()
    
    # Questions for hip fracture
    hip_questions = [
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=hip_fracture_q.id,
            question_text="Patient age at admission",
            question_type=QuestionType.NUMERIC,
            order=1,
            is_required=True,
            validation={"min": 0, "max": 120},
        ),
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=hip_fracture_q.id,
            question_text="Time from admission to surgery (hours)",
            question_type=QuestionType.NUMERIC,
            order=2,
            is_required=True,
            validation={"min": 0, "max": 168},
        ),
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=hip_fracture_q.id,
            question_text="Type of fracture",
            question_type=QuestionType.CATEGORICAL,
            order=3,
            is_required=True,
            options={"choices": ["Intracapsular", "Extracapsular", "Subtrochanteric"]},
        ),
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=hip_fracture_q.id,
            question_text="Mobilised within 24 hours post-op?",
            question_type=QuestionType.BOOLEAN,
            order=4,
            is_required=True,
        ),
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=hip_fracture_q.id,
            question_text="Complications",
            question_type=QuestionType.MULTI_SELECT,
            order=5,
            is_required=False,
            options={"choices": ["None", "Infection", "DVT/PE", "Delirium", "Pneumonia", "Death"]},
        ),
    ]
    
    for q in hip_questions:
        db.add(q)
    
    # Stroke Audit Questionnaire
    stroke_q = Questionnaire(
        id=str(uuid.uuid4()),
        title="Acute Stroke Care Quality",
        description="SSNAP (Sentinel Stroke National Audit Programme) style audit",
        version=1,
        created_by_id=audit_lead.id,
        site_id=sites[1].id,
        is_published=True,
    )
    db.add(stroke_q)
    await db.flush()
    
    stroke_questions = [
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=stroke_q.id,
            question_text="Time from symptom onset to arrival (minutes)",
            question_type=QuestionType.NUMERIC,
            order=1,
            is_required=True,
            validation={"min": 0, "max": 10080},
        ),
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=stroke_q.id,
            question_text="CT scan performed within 1 hour?",
            question_type=QuestionType.BOOLEAN,
            order=2,
            is_required=True,
        ),
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=stroke_q.id,
            question_text="Thrombolysis given?",
            question_type=QuestionType.BOOLEAN,
            order=3,
            is_required=True,
        ),
        Question(
            id=str(uuid.uuid4()),
            questionnaire_id=stroke_q.id,
            question_text="Modified Rankin Scale at discharge",
            question_type=QuestionType.CATEGORICAL,
            order=4,
            is_required=True,
            options={"choices": ["0", "1", "2", "3", "4", "5", "6 (Death)"]},
        ),
    ]
    
    for q in stroke_questions:
        db.add(q)
    
    await db.commit()
    
    print(f"✅ Created 2 questionnaires with questions")
    return [hip_fracture_q, stroke_q]


async def create_audits(db: AsyncSession, users: list[User], sites: list[Site], questionnaires: list[Questionnaire]) -> list[Audit]:
    """Create sample audits."""
    
    audits = [
        Audit(
            id=str(uuid.uuid4()),
            title="Q4 2024 Hip Fracture Outcomes",
            description="Quarterly audit of hip fracture care pathway compliance and outcomes",
            lead_id=users[2].id,  # Audit lead
            site_id=sites[0].id,
            questionnaire_id=questionnaires[0].id,
            start_date=datetime.now() - timedelta(days=90),
            end_date=datetime.now() + timedelta(days=90),
            status=AuditStatus.ACTIVE,
            is_open=True,
        ),
        Audit(
            id=str(uuid.uuid4()),
            title="Stroke Care Quality Improvement",
            description="Ongoing stroke care pathway audit focusing on door-to-needle times",
            lead_id=users[2].id,
            site_id=sites[1].id,
            questionnaire_id=questionnaires[1].id,
            start_date=datetime.now() - timedelta(days=60),
            end_date=datetime.now() + timedelta(days=120),
            status=AuditStatus.ACTIVE,
            is_open=True,
        ),
        Audit(
            id=str(uuid.uuid4()),
            title="Sepsis Recognition and Treatment",
            description="Audit of sepsis 6 bundle compliance in ED",
            lead_id=users[2].id,
            site_id=sites[0].id,
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now() + timedelta(days=60),
            status=AuditStatus.PLANNING,
            is_open=False,
        ),
    ]
    
    for audit in audits:
        db.add(audit)
    
    await db.commit()
    
    print(f"✅ Created {len(audits)} audits")
    return audits


async def create_sample_episodes(db: AsyncSession, audits: list[Audit], questionnaires: list[Questionnaire], sites: list[Site]):
    """Create sample audit episodes (patient data)."""
    
    # Hip fracture episodes
    hip_episodes = []
    for i in range(15):
        episode = AuditEpisode(
            id=str(uuid.uuid4()),
            audit_id=audits[0].id,
            questionnaire_id=questionnaires[0].id,
            site_id=sites[0].id,
            pseudonym=f"HF-2024-{str(i+1).zfill(4)}",
            responses={
                "age": 75 + i,
                "time_to_surgery": 18 + (i * 2),
                "fracture_type": ["Intracapsular", "Extracapsular", "Subtrochanteric"][i % 3],
                "mobilised_24h": i % 3 != 0,
                "complications": ["None"] if i % 4 == 0 else ["Delirium", "Pneumonia"][:(i % 2) + 1],
            },
            submitted_at=datetime.now() - timedelta(days=i),
        )
        hip_episodes.append(episode)
        db.add(episode)
    
    # Stroke episodes
    stroke_episodes = []
    for i in range(10):
        episode = AuditEpisode(
            id=str(uuid.uuid4()),
            audit_id=audits[1].id,
            questionnaire_id=questionnaires[1].id,
            site_id=sites[1].id,
            pseudonym=f"STR-2024-{str(i+1).zfill(4)}",
            responses={
                "time_to_arrival": 45 + (i * 15),
                "ct_within_hour": i % 2 == 0,
                "thrombolysis": i % 3 == 0,
                "rankin_score": str(i % 6),
            },
            submitted_at=datetime.now() - timedelta(days=i * 2),
        )
        stroke_episodes.append(episode)
        db.add(episode)
    
    await db.commit()
    
    print(f"✅ Created {len(hip_episodes) + len(stroke_episodes)} sample episodes")


async def seed_database():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    print("⚠️  WARNING: This will delete all existing data!")
    print()
    
    async with AsyncSessionLocal() as db:
        # Clear existing data
        print("🗑️  Clearing existing data...")
        await db.execute(text("TRUNCATE TABLE audit_episodes CASCADE"))
        await db.execute(text("TRUNCATE TABLE questions CASCADE"))
        await db.execute(text("TRUNCATE TABLE questionnaires CASCADE"))
        await db.execute(text("TRUNCATE TABLE audits CASCADE"))
        await db.execute(text("TRUNCATE TABLE user_sites CASCADE"))
        await db.execute(text("TRUNCATE TABLE users CASCADE"))
        await db.execute(text("TRUNCATE TABLE sites CASCADE"))
        await db.commit()
        print("✅ Existing data cleared")
        print()
        
        # Create all entities
        sites = await create_sites(db)
        users = await create_users(db, sites)
        questionnaires = await create_questionnaires(db, users[2], sites)  # Audit lead creates questionnaires
        audits = await create_audits(db, users, sites, questionnaires)
        await create_sample_episodes(db, audits, questionnaires, sites)
    
    print()
    print("✨ Database seeding complete!")
    print()
    print("You can now:")
    print("  - Login with any of the users listed above")
    print("  - View sample audits and questionnaires")
    print("  - Test data entry with pre-populated episodes")
    print("  - Explore analytics with real data")


if __name__ == "__main__":
    asyncio.run(seed_database())
