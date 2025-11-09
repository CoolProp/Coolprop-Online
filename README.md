Coolprop-Online
===============

The source code of the online version of CoolProp

## Migration from web2py to py4web

This application has been migrated from web2py to py4web. The migration includes:

### Key Changes

1. **Project Structure**:
   - `models/db.py` → `models.py` and `common.py`
   - `controllers/default.py` → `controllers.py` with `@action` decorators
   - `views/` → `templates/` (py4web convention)
   - Added `settings.py` for configuration

2. **Controllers**:
   - Converted from web2py function-based controllers to py4web action decorators
   - Changed `def index():` to `@action("index")` pattern
   - Updated `URL()` function calls to use py4web's URL helper
   - Replaced `redirect()` and `request` with py4web equivalents

3. **Forms**:
   - Migrated from web2py's `FORM()` processing to manual form handling
   - Form validation moved to separate functions
   - Updated form submission handling for py4web's request/response model

4. **Templates**:
   - Converted from `{{}}` syntax (web2py) to `[[]]` syntax (py4web)
   - Updated `extend` and `include` directives
   - Replaced Bootstrap 2.x with Bootstrap 5.x for modern styling

5. **Authentication**:
   - Migrated from web2py Auth to py4web Auth
   - Auth routes now use `@action.uses(auth.plugin)`

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   py4web run apps
   ```

3. Access at: `http://localhost:8000/coolpropgit`

### Dependencies

- py4web >= 1.20240906.1
- CoolProp >= 6.4.0
- numpy >= 1.21.0
- matplotlib >= 3.4.0
- mpld3 >= 0.5.0

### Notes

- The application uses SQLite for database storage (sessions and auth)
- Static files are served from the `static/` directory
- Database files are stored in `databases/`
- Session files are stored in `sessions/`
