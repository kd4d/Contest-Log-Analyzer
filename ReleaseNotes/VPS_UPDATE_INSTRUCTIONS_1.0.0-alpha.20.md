# VPS Update Instructions: v1.0.0-alpha.20

**Release Date:** June 18, 2026  
**Target Version:** v1.0.0-alpha.20

---

## Production Server (Hostinger)

| Item | Value |
|------|--------|
| **URL** | https://cla.kd4d.org |
| **Hostinger login** | hPanel — Google sign-in (`kd4d@kd4d.org`) |
| **Access** | Hostinger **Docker Manager** or VPS browser/SSH terminal |
| **Server** | `srv1269198` (Debian) |
| **Project path** | `/docker/Contest-Log-Analyzer` |

**Do not** run git commands in `/docker` alone — the repository is in `/docker/Contest-Log-Analyzer`.

Full Hostinger details: [Docs/InstallationGuide.md](../Docs/InstallationGuide.md) Section 3.0.

---

## Quick Update (3 Commands)

**Open Docker Manager (or SSH) on the Hostinger VPS and run:**

```bash
cd /docker/Contest-Log-Analyzer
git fetch --tags origin
git checkout v1.0.0-alpha.20
docker compose up --build -d
```

**Note:** If you use a custom compose file on the server, add `-f docker-compose.prod.yml` to the `docker compose` commands.

---

## What These Commands Do

1. **`cd /docker/Contest-Log-Analyzer`** - Navigate to your installation directory
2. **`git fetch --tags origin`** - Download the latest tags from GitHub
3. **`git checkout v1.0.0-alpha.20`** - Switch to the v1.0.0-alpha.20 release
4. **`docker compose up --build -d`** - Rebuild the Docker image with new code and restart containers in detached mode

The `--build` flag rebuilds the Docker image with the new code, and `-d` runs containers in the background. Old containers are automatically stopped and new ones started.

---

## Verify the Update

After running the update commands:

1. **Check that containers are running:**
   ```bash
   cd /docker/Contest-Log-Analyzer
   docker compose ps
   ```
   You should see the `web` container (often named `contest-log-analyzer-web-1`) with status "Up". Hostinger **Docker Manager** should also show the container running.

2. **Check the logs for any errors:**
   ```bash
   docker compose logs web
   ```
   Look for any error messages. The application should start normally.

3. **Visit your website:**
   - Open https://cla.kd4d.org (or your site URL)
   - Run an IARU-HF or WRTC comparison and open a missed multipliers text report
   - Confirm `(P/Run)` or `(P/Run/CW)` appears where cross-band passes apply
   - Confirm multi-mode cells still show aligned `(Run/CW)` / `(S&P/PH)` slots

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

### 504 Gateway Timeout During Analysis

If upload fails after progress reaches **Generating**, increase nginx proxy timeouts on the host. See [Installation Guide](../Docs/InstallationGuide.md) Section 3.3 (504 Gateway Timeout).

### Rollback to Previous Version

If you need to rollback to the previous version (v1.0.0-alpha.19):

```bash
cd /docker/Contest-Log-Analyzer
git checkout v1.0.0-alpha.19
docker compose up --build -d
```

---

## What's New in This Release

- **Missed multipliers (P/ pass flag):** HQ, IARU Officials, and DXCC on per-band tables
- **Hostinger production docs:** Section 3.0 in Installation Guide
- **nginx 504 troubleshooting** for long report generation

---

## After Update

- **No action required** for most users
- **No data migration needed**
- Regenerate missed multiplier reports to see `(P/...)` flags

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
- Missed multiplier reports show `(P/...)` where cross-band passes apply (when regenerated)
