-- Learning Management Service — Database Initialization
-- This script runs automatically on the first start of the PostgreSQL container.
-- Tables start empty — all data is populated via the ETL pipeline.

-- Item: learning materials organized as a tree (labs → tasks).
-- The tree structure uses the adjacency list pattern (parent_id).
-- Type-specific attributes are stored in a JSONB column.
CREATE TABLE IF NOT EXISTS item (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL DEFAULT 'step',
    parent_id INTEGER REFERENCES item(id),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    attributes JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Learner: students identified by anonymized external IDs
CREATE TABLE IF NOT EXISTS learner (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) NOT NULL UNIQUE,
    student_group VARCHAR(255) NOT NULL DEFAULT '',
    enrolled_at TIMESTAMP DEFAULT NULL
);

-- Interacts: records of learners interacting with items (check submissions)
CREATE TABLE IF NOT EXISTS interacts (
    id SERIAL PRIMARY KEY,
    external_id INTEGER UNIQUE,
    learner_id INTEGER NOT NULL REFERENCES learner(id),
    item_id INTEGER NOT NULL REFERENCES item(id),
    kind VARCHAR(50) NOT NULL,
    score DOUBLE PRECISION,
    checks_passed INTEGER,
    checks_total INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Seed data for testing (labs, tasks, learners, and interactions)
-- Labs
INSERT INTO item (type, parent_id, title) VALUES
('lab', NULL, 'Lab 01 – Products, Architecture & Roles'),
('lab', NULL, 'Lab 02 — Run, Fix, and Deploy a Backend Service'),
('lab', NULL, 'Lab 03 — Backend API: Explore, Debug, Implement, Deploy'),
('lab', NULL, 'Lab 04 — Testing, Front-end, and AI Agents'),
('lab', NULL, 'Lab 05 — Data Pipeline and Analytics Dashboard'),
('lab', NULL, 'Lab 06 — Build Your Own Agent');

-- Tasks for Lab 01 (parent_id = 1)
INSERT INTO item (type, parent_id, title) VALUES
('task', 1, 'Lab setup'),
('task', 1, 'Task 0: Practice the Git workflow'),
('task', 1, 'Task 1: Product & architecture description');

-- Tasks for Lab 02 (parent_id = 2)
INSERT INTO item (type, parent_id, title) VALUES
('task', 2, 'Lab setup'),
('task', 2, 'Task 1: Run the web server'),
('task', 2, 'Task 2: Identify, report, and fix a bug'),
('task', 2, 'Task 3: Run the web server using Docker Compose'),
('task', 2, 'Task 4: Deploy the web server to the VM');

-- Tasks for Lab 04 (parent_id = 4)
INSERT INTO item (type, parent_id, title) VALUES
('task', 4, 'Lab setup'),
('task', 4, 'Task 1: Observe System Component Interaction'),
('task', 4, 'Task 2: Back-end Testing'),
('task', 4, 'Task 3: Add Front-end');

-- Learners
INSERT INTO learner (external_id, student_group) VALUES
('student_001', 'B21-01'),
('student_002', 'B21-01'),
('student_003', 'B21-02'),
('student_004', 'B21-02'),
('student_005', 'B21-03');

-- Interactions for Lab 01 tasks (item_id 7,8,9)
INSERT INTO interacts (learner_id, item_id, kind, score, checks_passed, checks_total) VALUES
(1, 7, 'submission', 100, 1, 1), (1, 8, 'submission', 100, 1, 1), (1, 9, 'submission', 85, 1, 1),
(2, 7, 'submission', 100, 1, 1), (2, 8, 'submission', 100, 1, 1), (2, 9, 'submission', 90, 1, 1),
(3, 7, 'submission', 100, 1, 1), (3, 8, 'submission', 50, 0, 1), (3, 9, 'submission', 75, 1, 1),
(4, 7, 'submission', 100, 1, 1), (4, 8, 'submission', 100, 1, 1), (4, 9, 'submission', 95, 1, 1),
(5, 7, 'submission', 100, 1, 1), (5, 8, 'submission', 100, 1, 1), (5, 9, 'submission', 80, 1, 1);

-- Interactions for Lab 02 tasks (item_id 10,11,12,13,14)
INSERT INTO interacts (learner_id, item_id, kind, score, checks_passed, checks_total) VALUES
(1, 10, 'submission', 100, 1, 1), (1, 11, 'submission', 100, 1, 1), (1, 12, 'submission', 100, 1, 1), (1, 13, 'submission', 80, 1, 1), (1, 14, 'submission', 100, 1, 1),
(2, 10, 'submission', 100, 1, 1), (2, 11, 'submission', 100, 1, 1), (2, 12, 'submission', 50, 0, 1), (2, 13, 'submission', 100, 1, 1), (2, 14, 'submission', 100, 1, 1),
(3, 10, 'submission', 100, 1, 1), (3, 11, 'submission', 100, 1, 1), (3, 12, 'submission', 100, 1, 1), (3, 13, 'submission', 60, 0, 1), (3, 14, 'submission', 50, 0, 1),
(4, 10, 'submission', 100, 1, 1), (4, 11, 'submission', 100, 1, 1), (4, 12, 'submission', 100, 1, 1), (4, 13, 'submission', 100, 1, 1), (4, 14, 'submission', 100, 1, 1),
(5, 10, 'submission', 100, 1, 1), (5, 11, 'submission', 100, 1, 1), (5, 12, 'submission', 100, 1, 1), (5, 13, 'submission', 100, 1, 1), (5, 14, 'submission', 100, 1, 1);

-- Interactions for Lab 04 tasks (item_id 15,16,17,18)
INSERT INTO interacts (learner_id, item_id, kind, score, checks_passed, checks_total) VALUES
(1, 15, 'submission', 100, 1, 1), (1, 16, 'submission', 100, 1, 1), (1, 17, 'submission', 100, 1, 1), (1, 18, 'submission', 80, 1, 1),
(2, 15, 'submission', 100, 1, 1), (2, 16, 'submission', 100, 1, 1), (2, 17, 'submission', 50, 0, 1), (2, 18, 'submission', 100, 1, 1),
(3, 15, 'submission', 100, 1, 1), (3, 16, 'submission', 100, 1, 1), (3, 17, 'submission', 100, 1, 1), (3, 18, 'submission', 60, 0, 1),
(4, 15, 'submission', 100, 1, 1), (4, 16, 'submission', 100, 1, 1), (4, 17, 'submission', 100, 1, 1), (4, 18, 'submission', 100, 1, 1),
(5, 15, 'submission', 100, 1, 1), (5, 16, 'submission', 100, 1, 1), (5, 17, 'submission', 100, 1, 1), (5, 18, 'submission', 100, 1, 1);
