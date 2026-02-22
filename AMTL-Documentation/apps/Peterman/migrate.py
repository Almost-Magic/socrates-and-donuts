"""Database migration script - Phase 2 Chambers."""
from app.config import config
from sqlalchemy import create_engine, text
import sys

engine = create_engine(config['DB_URL'])

# Tables to create - each in its own transaction
tables = [
    ('semantic_gravity_records', '''
        CREATE TABLE IF NOT EXISTS semantic_gravity_records (
            id SERIAL PRIMARY KEY,
            domain_id UUID REFERENCES domains(domain_id),
            measured_at TIMESTAMP DEFAULT NOW(),
            sgs_score FLOAT NOT NULL,
            cluster_count INTEGER DEFAULT 0,
            avg_similarity FLOAT DEFAULT 0.0,
            drift_delta FLOAT DEFAULT 0.0,
            cluster_details JSON
        )
    '''),
    ('lcri_records', '''
        CREATE TABLE IF NOT EXISTS lcri_records (
            id SERIAL PRIMARY KEY,
            domain_id UUID REFERENCES domains(domain_id),
            page_url TEXT NOT NULL,
            measured_at TIMESTAMP DEFAULT NOW(),
            lcri_score FLOAT NOT NULL,
            summarisation_score FLOAT DEFAULT 0.0,
            citation_probability FLOAT DEFAULT 0.0,
            snippet_strength FLOAT DEFAULT 0.0,
            rag_compatibility FLOAT DEFAULT 0.0,
            test_details JSON,
            model_version VARCHAR(50) DEFAULT 'KNW-004'
        )
    '''),
    ('authority_records', '''
        CREATE TABLE IF NOT EXISTS authority_records (
            id SERIAL PRIMARY KEY,
            domain_id UUID REFERENCES domains(domain_id),
            topic TEXT NOT NULL,
            measured_at TIMESTAMP DEFAULT NOW(),
            authority_score INTEGER DEFAULT 0,
            mentioned VARCHAR(10) DEFAULT 'no',
            rank_position INTEGER DEFAULT 0,
            competitors_mentioned JSON,
            details JSON
        )
    '''),
    ('performance_records', '''
        CREATE TABLE IF NOT EXISTS performance_records (
            id SERIAL PRIMARY KEY,
            domain_id UUID REFERENCES domains(domain_id),
            content_id VARCHAR(100),
            content_title VARCHAR(500),
            measured_at TIMESTAMP DEFAULT NOW(),
            sov_score FLOAT DEFAULT 0.0,
            sov_delta FLOAT DEFAULT 0.0,
            sgs_delta FLOAT DEFAULT 0.0,
            lcri_actual FLOAT DEFAULT 0.0,
            lcri_predicted FLOAT DEFAULT 0.0,
            citation_velocity INTEGER DEFAULT 0,
            cannibalisation_score FLOAT DEFAULT 0.0,
            details JSON
        )
    '''),
    ('competitor_domains', '''
        CREATE TABLE IF NOT EXISTS competitor_domains (
            id SERIAL PRIMARY KEY,
            domain_id UUID REFERENCES domains(domain_id),
            competitor_url VARCHAR(500) NOT NULL,
            competitor_name VARCHAR(255),
            threat_level INTEGER DEFAULT 1,
            last_scanned TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )
    '''),
    ('oracle_forecasts', '''
        CREATE TABLE IF NOT EXISTS oracle_forecasts (
            id SERIAL PRIMARY KEY,
            domain_id UUID REFERENCES domains(domain_id),
            generated_at TIMESTAMP DEFAULT NOW(),
            forecast_days INTEGER DEFAULT 90,
            topics JSON,
            calendar JSON,
            confidence FLOAT DEFAULT 0.0
        )
    '''),
    ('perception_records', '''
        CREATE TABLE IF NOT EXISTS perception_records (
            id SERIAL PRIMARY KEY,
            domain_id UUID REFERENCES domains(domain_id),
            measured_at TIMESTAMP DEFAULT NOW(),
            sentiment_score FLOAT DEFAULT 50.0,
            narrative_score FLOAT DEFAULT 50.0,
            claim_count INTEGER DEFAULT 0,
            negative_claims INTEGER DEFAULT 0,
            positive_claims INTEGER DEFAULT 0,
            details JSON
        )
    '''),
    ('deployments', '''
        CREATE TABLE IF NOT EXISTS deployments (
            id SERIAL PRIMARY KEY,
            domain_id UUID REFERENCES domains(domain_id),
            brief_id INTEGER,
            status VARCHAR(20) DEFAULT 'pending',
            pre_snapshot JSON,
            post_snapshot JSON,
            deployed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW()
        )
    '''),
]

for table_name, create_sql in tables:
    try:
        with engine.connect() as conn:
            conn.execute(text(create_sql))
            conn.commit()
            print(f'[OK] Created {table_name}')
    except Exception as e:
        print(f'[FAIL] {table_name}: {e}')

print('\nMigration complete!')
