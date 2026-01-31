# VPS Update Instructions: v1.0.0-alpha.18

**Release Date:** January 31, 2026  
**Target Version:** v1.0.0-alpha.18

---

## Quick Update (3 Commands)

**SSH into your VPS and run these commands:**

```bash
cd /docker/Contest-Log-Analyzer
git fetch --tags origin
git checkout v1.0.0-alpha.18
docker compose up --build -d
```

**Note:** Adjust the path (`/docker/Contest-Log-Analyzer`) to match your installation directory. If you're using a custom compose file name, add `-f docker-compose.prod.yml` (or your filename) to the docker compose command.

---

## What These Commands Do

1. **`cd /docker/Contest-Log-Analyzer`** - Navigate to your installation directory
2. **`git fetch --tags origin`** - Download the latest tags from GitHub
3. **`git checkout v1.0.0-alpha.18`** - Switch to the v1.0.0-alpha.18 release
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
   - Test QSO Dashboard: upload two logs and open the Rate Differential pane; confirm Cumulative Difference plot and summary table are fully visible (no truncation) and grid lines are capped
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

If you need to rollback to the previous version (v1.0.0-alpha.17):

```bash
cd /docker/Contest-Log-Analyzer
git checkout v1.0.0-alpha.17
docker compose up --build -d
```

---

## What's New in This Release

- **Rate Chart report** – New plot showing QSO or Points rate (hourly) as a grouped bar chart for 1–3 logs
- **Bar Graph in Rate Differential** – QSO Dashboard Rate Differential pane now offers both Cumulative Difference and Bar Graph (Rate Chart) options
- **Cumulative Difference fixes** – Hard cap of 15 horizontal grid lines; overflow/infinity handling in axis math; Rate Differential pane uses fixed-size + scrollable viewport so the summary table below the plot is no longer truncated
- **Contest definitions** – Single-mode contest names now include mode (e.g. CQ 160 CW/SSB, ARRL SS CW/PH, NAQP CW/PH/RTTY)
- **Report drawer** – Overlay opens correctly when clicking report links in the report list
- **Diagnostics** – Removed temporary QSO Dashboard diagnostic log messages

---

## After Update

- **No action required** – All changes are automatically applied
- **No data migration needed** – No database or report format changes
- **Existing reports continue to work** – No breaking changes

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
- QSO Dashboard Rate Differential pane shows Cumulative Difference and Bar Graph; table below plot is fully visible
