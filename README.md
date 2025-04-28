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
6. **Update database (optional)**
   ```bash
   python manage.py data
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the app**
   Open your browser and go to: [http://127.0.0.1:8000/polls](http://127.0.0.1:8000/polls)

## Data & Legal
Polling data is taken directly from **https://api.dawum.de/**. 
Data source: dawum.de (Open Database License (ODbL odbl.dawum.de))

## Usage

- Visit the homepage to view polls
- Log in as an admin to create and manage polls
