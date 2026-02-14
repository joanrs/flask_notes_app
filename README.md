# Flask Notes Application

A simple note-taking application with Flask, SQLAlchemy, and SQLite.

## Features

- **Notes Management**: Create, read, update, and delete notes
- **Categories**: Organize notes with colored categories
- **Attachments**: Upload images, documents, and files to notes
- **Likes**: Like your favorite notes
- **Multiple Views**: Table view and Google Keep-style card view
- **Responsive Design**: Works on mobile and desktop

## Installation

1. **Clone the repository** (or download the files):

```bash
cd flask_notes_app
```

2. **Create a virtual environment** (recommended):

```bash
python3 -m venv venv
```

3. **Activate the virtual environment**:

- **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

- **Windows**:
  ```bash
  venv\Scripts\activate
  ```

4. **Install dependencies**:

```bash
pip install -r requirements.txt
```

**OR use the setup script (recommended)**:

```bash
./setup_and_run.sh
```

This script will automatically:
- Create the virtual environment if it doesn't exist
- Activate it
- Install all dependencies
- Create necessary directories
- Run the application

4. **Run the application**:

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Creating Notes
1. Click "New Note" in the navigation bar
2. Fill in title, content, and select a category
3. Optionally upload attachments (images, documents, etc.)
4. Click "Save Note"

### Managing Categories
1. Go to "Categories" in the navigation
2. Create new categories with custom colors
3. Edit or delete existing categories (can't delete categories with notes)

### Views
- **Table View**: Traditional table layout with all note details
- **Keep View**: Card-based layout similar to Google Keep

### Attachments
- Upload multiple files per note
- Supported formats: PNG, JPG, JPEG, GIF, PDF, TXT, DOC, DOCX
- View and download attachments from note details
- Delete individual attachments

## Configuration

Edit the `.env` file to customize:
- `SECRET_KEY`: Change this for production
- `DATABASE_URL`: SQLite database location
- `UPLOAD_FOLDER`: Where to store uploaded files

## Database

The application uses SQLite by default. The database file `notes.db` will be created automatically in the project root.

## Screenshots

![Table View](screenshots/table_view.png)
![Keep View](screenshots/keep_view.png)
![Note Details](screenshots/note_details.png)

## License

MIT License - Free to use and modify.

## Roadmap

- User authentication
- Search functionality
- Note sharing
- Export/import notes
- Dark mode