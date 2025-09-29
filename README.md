# AsiriaPOS Frontend

This is the frontend for **AsiriaPOS**, a Point of Sale (POS) web application designed for small businesses. The app provides an intuitive interface for managing sales, inventory, purchases, expenses, and business reports.

## Features

- **Dashboard**: Overview of key business metrics.
- **POS (Point of Sale)**: Fast, interactive sales interface with cart, checkout, and payment method selection.
- **Inventory Management**: Add, edit, delete, and search products. View stock levels and reorder alerts.
- **Purchases**: Record and manage purchase orders from suppliers.
- **Sales**: Track and review sales transactions.
- **Expenses**: Log and categorize business expenses.
- **User Management**: Manage users and permissions.
- **Reports**: Generate business reports for analysis.
- **Dynamic API Integration**: Frontend communicates with a backend API for real-time data.

## Tech Stack

- **Django**: Backend framework for serving templates and static files.
- **HTML/CSS/JS**: Modern, responsive UI using Bootstrap 5 and Tabler Icons.
- **Vite**: Fast frontend build tool for asset bundling and hot reload.
- **PostCSS**: CSS processing with autoprefixer and cssnano for production.
- **Docker**: Containerized development and deployment.
- **Nginx**: Reverse proxy for serving static files and app.

## Project Structure

- `templates/pages/` — Main HTML templates for each app section (POS, inventory, purchases, etc.)
- `static/assets/` — CSS, JS, and image assets.
- `apps/pages/views.py` — Django views for rendering frontend pages.
- `vite.config.js` — Vite configuration for frontend asset building.
- `Dockerfile`, `docker-compose.yml` — Containerization setup.
- `manage.py`, `config/settings.py` — Django project configuration.

## Development

1. **Install dependencies**  
   ```bash
   npm install
   ```

2. **Run frontend build in development mode**  
   ```bash
   npm run dev
   ```

3. **Run Django server**  
   ```bash
   python manage.py runserver
   ```

4. **Or use Docker Compose**  
   ```bash
   docker-compose up --build
   ```

## Status

AsiriaPOS frontend is under active development.  
- POS, Inventory, Purchases, Sales, Expenses, User Management, and Reports pages are scaffolded.
- Inventory and POS pages have interactive UI and basic API integration.
- Further enhancements and backend integration are ongoing.

## License

See [LICENSE.md](LICENSE.md) for details.

