# Polls

Polls is a Django-based web application that allows users to create, vote on, and view results for simple polls.

## Features

- Create, edit, and delete polls with multiple choices
- Vote on polls and see real-time results
- Admin panel for managing polls and users
- Clean, responsive design

## Tech Stack

- Python 3
- Django
- SQLite
- HTML, CSS, JavaScript

## Getting Started

Follow these instructions to set up and run the project locally.

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vladischul/polls.git
   cd polls
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv env
   source env/Scripts/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the app**
   Open your browser and go to: [http://127.0.0.1:8000/polls](http://127.0.0.1:8000/polls)

## Usage

- Visit the homepage to view and vote on polls
- Log in as an admin to create and manage polls
- Results are updated in real-time after voting