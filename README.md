# AI Influencer Manager

A private Flask admin website for managing AI influencer personas, generated images, videos, captions, and Instagram-ready content exports.

The first version should focus on organizing and reviewing content, not auto-posting. The intended workflow is:

1. Create an AI persona.
2. Upload or generate media assets.
3. Review and approve assets.
4. Attach captions and posting notes.
5. Push approved content to the persona profile page.
6. Download the final image/video and manually upload it to Instagram.

## Recommended Tech Stack

- **Backend:** Python + Flask
- **Database:** SQLite for local v1, PostgreSQL for production
- **ORM:** Flask-SQLAlchemy
- **Authentication:** Flask-Login
- **Forms:** Flask-WTF
- **Image utilities:** Pillow
- **Environment config:** python-dotenv
- **Frontend:** Server-rendered Jinja templates
- **Styling:** Bootstrap or Tailwind CSS
- **File storage:** Local uploads folder for v1, S3 or Cloudflare R2 later

## Phase Roadmap

### Phase 1: Project Setup

Create the base Flask app structure and local development environment.

- Create a Python virtual environment.
- Install Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Pillow, and python-dotenv.
- Add basic app configuration for secret key, database URL, upload folder, and allowed media types.
- Create the first Flask app factory and dashboard route.
- Set up folders for routes, models, templates, static files, and uploads.

### Phase 2: Authentication and Admin Access

Make the app private by default.

- Add admin login and logout.
- Create one initial admin user.
- Protect all dashboard routes with login requirements.
- Store passwords securely using hashing.
- Redirect unauthenticated users to the login page.

### Phase 3: Persona Management

Add CRUD pages for AI influencer personas.

Each persona should store:

- Name
- Niche
- Bio
- Personality
- Visual style
- Caption tone
- Reference notes
- Optional reference image
- Active/inactive status

The persona page should become the source of truth for identity consistency.

### Phase 4: Asset Library

Add upload and organization tools for generated media.

- Support image and video uploads.
- Link every asset to a persona.
- Track media type: image or video.
- Track status: draft, approved, rejected, ready to post, posted.
- Store prompt, caption idea, generation notes, and upload date.
- Show thumbnails or previews in the admin dashboard.

### Phase 5: Captions and Post Planning

Add caption and content planning records.

- Create captions linked to personas and optional media assets.
- Create post records with platform, scheduled date, caption, selected image/video, and manual posting status.
- Build a simple dashboard showing upcoming posts and ready-to-post content.
- Track whether a post has already been uploaded manually.

### Phase 6: Persona Profile Pages

Create private profile pages for each AI influencer.

- Show only approved or ready-to-post assets.
- Display persona details and approved content.
- Add download buttons for images and videos.
- Add copyable captions for manual Instagram upload.
- Keep rejected and draft content hidden from profile pages.

### Phase 7: Review Workflow

Add an approval process before content reaches profile pages.

- Build a review queue for draft assets.
- Allow the admin to approve or reject media.
- Add rejection notes.
- Allow approved content to be marked as ready to post.
- Ensure only approved or ready-to-post content can appear on persona profile pages.

### Phase 8: UI Improvement

Improve usability once the main workflow works.

- Add Bootstrap or Tailwind CSS.
- Improve dashboard layout.
- Add filters by persona, status, date, and media type.
- Add media thumbnails.
- Add preview modals.
- Add empty states for personas, assets, captions, and posts.

### Phase 9: AI Generation Integration

Add optional generation features after the manual workflow is stable.

- Integrate external APIs for image, video, or caption generation.
- Save prompts and generation settings.
- Keep generated media in draft status until manually approved.
- Add prompt templates for consistent persona style.
- Store generation errors and retry notes when needed.

### Phase 10: Production Readiness

Prepare the app for real hosting and long-term use.

- Move from SQLite to PostgreSQL.
- Move local uploads to S3, Cloudflare R2, or similar object storage.
- Add database and media backups.
- Add role-based users if more than one admin is needed.
- Configure production environment variables.
- Deploy to a VPS, Render, Railway, Fly.io, or a similar hosting provider.

## Core Database Models

### User

Represents the admin account.

Suggested fields:

- `id`
- `email`
- `password_hash`
- `is_admin`
- `created_at`

### Persona

Represents one AI influencer identity.

Suggested fields:

- `id`
- `name`
- `niche`
- `bio`
- `personality`
- `visual_style`
- `caption_tone`
- `reference_notes`
- `reference_image_path`
- `is_active`
- `created_at`
- `updated_at`

### MediaAsset

Represents an uploaded or generated image/video.

Suggested fields:

- `id`
- `persona_id`
- `media_type`
- `file_path`
- `thumbnail_path`
- `status`
- `prompt`
- `caption_idea`
- `generation_notes`
- `created_at`
- `updated_at`

### Caption

Represents caption text for a persona or specific asset.

Suggested fields:

- `id`
- `persona_id`
- `media_asset_id`
- `text`
- `tone`
- `hashtags`
- `created_at`
- `updated_at`

### Post

Represents a planned or completed manual social post.

Suggested fields:

- `id`
- `persona_id`
- `media_asset_id`
- `caption_id`
- `platform`
- `scheduled_for`
- `status`
- `posted_at`
- `manual_posting_notes`
- `created_at`
- `updated_at`

### ReviewNote

Represents approval/rejection notes for media assets.

Suggested fields:

- `id`
- `media_asset_id`
- `user_id`
- `decision`
- `note`
- `created_at`

## Suggested Folder Structure

```text
ai-influencer-manager/
  app/
    __init__.py
    config.py
    extensions.py
    models.py
    auth/
      routes.py
      forms.py
    dashboard/
      routes.py
    personas/
      routes.py
      forms.py
    media/
      routes.py
      forms.py
    posts/
      routes.py
      forms.py
    templates/
      base.html
      auth/
      dashboard/
      personas/
      media/
      posts/
    static/
      css/
      js/
      uploads/
  migrations/
  tests/
  .env
  .gitignore
  requirements.txt
  run.py
  README.md
```

## Setup Commands

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF Pillow python-dotenv email-validator
```

Save dependencies:

```powershell
pip freeze > requirements.txt
```

Create a `.env` file:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=replace-this-with-a-long-random-secret
DATABASE_URL=sqlite:///app.db
UPLOAD_FOLDER=app/static/uploads
STORAGE_BACKEND=local
```

For production, optionally use PostgreSQL and S3-compatible storage:

```env
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:5432/database
STORAGE_BACKEND=s3
S3_BUCKET_NAME=your-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_ENDPOINT_URL=https://s3.amazonaws.com
```

Run the development server:

```powershell
flask run
```

Initialize the database:

```powershell
flask --app run.py init-db
```

Create the first admin user:

```powershell
flask --app run.py create-admin
```

## Default Product Decisions

- Use Flask instead of Django.
- Use SQLite for the first local version.
- Use local file storage first.
- Use server-rendered HTML templates.
- Use Bootstrap or Tailwind for styling.
- Keep Instagram upload manual for v1.
- Do not auto-post to Instagram in the first version.
- Keep the app private/admin-only by default.

## Test Plan

Before considering v1 complete, test:

- Admin login and logout.
- Protected dashboard access.
- Persona create, edit, and delete.
- Image upload.
- Video upload.
- Media status changes.
- Asset approval and rejection.
- Rejection note creation.
- Persona profile page visibility rules.
- Download links for approved images/videos.
- Caption creation and copy workflow.
- Post planning and status updates.
- Filtering by persona, status, date, and media type.

## Future Feature Ideas

- Prompt template library per persona.
- AI caption generation.
- AI image generation.
- AI video generation.
- Batch upload and batch approval.

## Optional OpenAI Caption Generation

To enable AI caption generation, set `OPENAI_API_KEY` in your `.env` file or environment.
Optionally set `OPENAI_MODEL` to use a different OpenAI chat model.
- Duplicate content detection.
- Content calendar view.
- Hashtag library.
- Brand safety checklist.
- Export ZIP packages for each post.
- Analytics notes for manually posted Instagram content.
- Multi-admin roles and permissions.
- Cloud storage and CDN support.

## Assumption

The first version is a private local/admin tool, not a public-facing influencer website. Public pages, automatic posting, and large-scale automation should come after the core admin workflow is stable.
