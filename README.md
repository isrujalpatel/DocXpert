# DocXpert — Smarter Documents, Instantly

DocXpert transforms the way you work with Word and PDF files — fix, format, convert, and perfect every document in seconds.

## Project Structure

```
DocXpert/
├── frontend/                    # Client-side application
│   ├── index.html               # Main landing page
│   ├── css/
│   │   ├── variables.css        # Design tokens & CSS custom properties
│   │   ├── base.css             # Reset, typography, global styles
│   │   ├── components/
│   │   │   ├── nav.css          # Navigation bar styles
│   │   │   ├── hero.css         # Hero section & macbook display
│   │   │   ├── kpi.css          # KPI / workflow step cards
│   │   │   ├── features.css     # Features grid section
│   │   │   ├── testimonials.css # Testimonials section
│   │   │   ├── closing.css      # Closing CTA section
│   │   │   └── footer.css       # Footer styles
│   │   ├── widgets.css          # Mini-doc, dropzone, chips, etc.
│   │   ├── animations.css       # All @keyframes & transitions
│   │   └── responsive.css       # Media queries & breakpoints
│   ├── js/
│   │   ├── app.js               # Main application entry point
│   │   ├── kpi-accordion.js     # KPI expanding card interactions
│   │   └── scroll-effects.js    # Scroll-based animations & effects
│   └── assets/
│       ├── images/              # Static images & icons
│       ├── fonts/               # Self-hosted fonts (if any)
│       └── icons/               # SVG icon files
│
├── backend/                     # Server-side application
│   ├── app.py                   # Flask/FastAPI app entry point
│   ├── requirements.txt         # Python dependencies
│   ├── config/
│   │   ├── settings.py          # App configuration & env vars
│   │   └── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py            # File upload endpoints
│   │   ├── convert.py           # DOC ↔ PDF conversion endpoints
│   │   ├── spelling.py          # Spelling check endpoints
│   │   ├── fonts.py             # Font normalization endpoints
│   │   ├── replace.py           # Find & replace endpoints
│   │   ├── compare.py           # Document comparison endpoints
│   │   └── export.py            # Final export/download endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_parser.py   # DOC/PDF parsing logic
│   │   ├── converter.py         # Format conversion service
│   │   ├── spell_checker.py     # AI spell-check service
│   │   ├── font_normalizer.py   # Font detection & normalization
│   │   ├── text_replacer.py     # Find & replace engine
│   │   ├── doc_comparator.py    # Document diff/comparison engine
│   │   └── file_manager.py      # Upload/download file management
│   ├── models/
│   │   ├── __init__.py
│   │   └── document.py          # Document data models
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py        # Input validation helpers
│   │   └── helpers.py           # General utility functions
│   └── tests/
│       ├── __init__.py
│       ├── test_upload.py
│       ├── test_convert.py
│       └── test_spelling.py
│
├── database/                    # Database layer
│   ├── migrations/              # Schema migration scripts
│   │   └── 001_initial.sql
│   ├── schema.sql               # Full database schema
│   └── seed.py                  # Seed/test data script
│
├── uploads/                     # Temporary uploaded files (gitignored)
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
├── docker-compose.yml           # Container orchestration (optional)
└── README.md                    # This file
```

## Getting Started

### Frontend
Open `frontend/index.html` in your browser, or serve it with any static file server.

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Environment Variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

## Tech Stack
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: Python (Flask/FastAPI)
- **Database**: SQLite (dev) / PostgreSQL (production)

## License
© 2025 DocXpert. All rights reserved.
