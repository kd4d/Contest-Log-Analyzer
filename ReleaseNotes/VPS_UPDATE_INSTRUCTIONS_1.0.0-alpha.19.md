# VPS Update Instructions: v1.0.0-alpha.19

**Release Date:** June 18, 2026  
**Target Version:** v1.0.0-alpha.19

---

## Quick Update (3 Commands)

**SSH into your VPS and run these commands:**

```bash
cd /docker/Contest-Log-Analyzer
git fetch --tags origin
git checkout v1.0.0-alpha.19
docker compose up --build -d
```

**Note:** Adjust the path (`/docker/Contest-Log-Analyzer`) to match your installation directory. If you're using a custom compose file name, add `-f docker-compose.prod.yml` (or your filename) to the docker compose command.

---

## What These Commands Do

1. **`cd /docker/Contest-Log-Analyzer`** - Navigate to your installation directory
2. **`git fetch --tags origin`** - Download the latest tags from GitHub
3. **`git checkout v1.0.0-alpha.19`** - Switch to the v1.0.0-alpha.19 release
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
   - Run a multi-mode comparison (e.g. IARU-HF) and open a missed multipliers text report; confirm cells show aligned `(Run/CW)` / `(S&P/PH)` slots where applicable
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

If you need to rollback to the previous version (v1.0.0-alpha.18):

```bash
cd /docker/Contest-Log-Analyzer
git checkout v1.0.0-alpha.18
docker compose up --build -d
```

---

## What's New in This Release

- **Missed multipliers text reports:** mode + Run/S&P aligned slots for multi-mode all-modes reports (IARU-HF, WRTC)
- **ARRL Sweepstakes** public log archive download
- **Run/S&P algorithm** documentation updates
- **RBN download script** and IARU 2025 daily archives

---

## After Update

- **No action required** for most users
- **No data migration needed**
- Regenerate missed multiplier reports to see new cell formatting on multi-mode contests

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
- Missed multiplier text reports show aligned mode slots on multi-mode contests (when applicable)
