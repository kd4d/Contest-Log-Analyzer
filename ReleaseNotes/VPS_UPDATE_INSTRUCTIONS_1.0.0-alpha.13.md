# VPS Update Instructions: v1.0.0-alpha.13

**Release Date:** January 26, 2026  
**Target Version:** v1.0.0-alpha.13

---

## Quick Update (3 Commands)

**SSH into your VPS and run these commands:**

```bash
cd /docker/Contest-Log-Analyzer
git fetch --tags origin
git checkout v1.0.0-alpha.13
docker compose up --build -d
```

**Note:** Adjust the path (`/docker/Contest-Log-Analyzer`) to match your installation directory. If you're using a custom compose file name, add `-f docker-compose.prod.yml` (or your filename) to the docker compose command.

---

## What These Commands Do

1. **`cd /docker/Contest-Log-Analyzer`** - Navigate to your installation directory
2. **`git fetch --tags origin`** - Download the latest tags from GitHub
3. **`git checkout v1.0.0-alpha.13`** - Switch to the v1.0.0-alpha.13 release
4. **`docker compose up --build -d`** - Rebuild the Docker image with new code and restart containers in detached mode

The `--build` flag rebuilds the Docker image with the new code, and `-d` runs containers in the background. Old containers are automatically stopped and new ones started.

---

## Verify the Update

After running the update commands:

1. **Check that containers are running:**
   ```bash
   docker compose ps
   ```
   You should see the `web` container with status "Up".

2. **Check the logs for any errors:**
   ```bash
   docker compose logs web
   ```
   Look for any error messages. The application should start normally.

3. **Visit your website:**
   - Open your browser and go to your site URL
   - The home page should show larger, bolder tab labels
   - Check that the site loads and functions normally

---

## If Something Goes Wrong

### Static Files (CSS/JS) Not Loading

If your site looks broken (missing styles, JavaScript not working):

```bash
docker compose exec web python web_app/manage.py collectstatic --noinput
```

(Add `-f docker-compose.prod.yml` if using a custom compose file)

### Database Migration Errors

If you see errors about unapplied migrations:

```bash
docker compose exec web python web_app/manage.py migrate
```

(Add `-f docker-compose.prod.yml` if using a custom compose file)

### Containers Won't Start

1. **Check logs for errors:**
   ```bash
   docker compose logs web
   ```

2. **Force recreate containers:**
   ```bash
   docker compose up --build --force-recreate -d
   ```

3. **View live logs:**
   ```bash
   docker compose logs -f web
   ```

### Rollback to Previous Version

If you need to rollback to the previous version (v1.0.0-alpha.12):

```bash
cd /docker/Contest-Log-Analyzer
git checkout v1.0.0-alpha.12
docker compose up --build -d
```

---

## What's New in This Release

- **Larger, bolder tab labels** on the home page for better visibility
- **Improved checkbox visibility** (darker borders)
- **Cleaner report layout** (removed unnecessary scrollbars)
- **Faster report loading** (replaced iframes with direct text rendering)
- **Fixed alignment issues** in QSO breakdown reports

---

## After Update

- **No action required** - All improvements are automatically applied
- **No data migration needed** - This is a UI improvement release
- **Existing reports continue to work** - No changes to report format

---

## Need Help?

If you encounter issues during the update:
1. Check the logs: `docker compose logs web`
2. Verify containers are running: `docker compose ps`
3. Try the troubleshooting steps above
4. If problems persist, you can rollback to the previous version (see above)

---

**Update completed successfully when:**
- Containers show status "Up" in `docker compose ps`
- Website loads normally in your browser
- You see the larger tab labels on the home page
