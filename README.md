## Inventory Manager

A tiny software for small business inventory management.  
Developed for my dad's shop as an alternative to all existing solutions which are too complex for him.

## Install


1. Clone repository
    ```bash
    git clone https://github.com/artenepo/inventory-manager
    ```
2. Install requirements
    ```bash
    pip3 install -r requirements.txt
    ```

3. Apply migrations
    ```bash
    python3 manage.py migrate
    ```

4. Create superuser
    ```bash
    python3 manage.py createsuperuser
    ```

5. Runserver
    ```bash
    python3 manage.py runserver
    ```

6. Open http://127.0.0.1:8000/ in you browser to access the website.  
Open http://127.0.0.1:8000/admin to access the admin panel