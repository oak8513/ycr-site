# DNS Setup for oakhem.com

Point these records at your domain registrar to connect oakhem.com to GitHub Pages.

## Required DNS Records

### A Records (root domain — oakhem.com)
Add all four:

| Type | Host | Value             | TTL  |
|------|------|-------------------|------|
| A    | @    | 185.199.108.153   | 3600 |
| A    | @    | 185.199.109.153   | 3600 |
| A    | @    | 185.199.110.153   | 3600 |
| A    | @    | 185.199.111.153   | 3600 |

### CNAME Record (www subdomain)

| Type  | Host | Value                  | TTL  |
|-------|------|------------------------|------|
| CNAME | www  | oak8513.github.io      | 3600 |

## After Adding DNS Records

1. DNS propagation takes 10 minutes to 48 hours
2. GitHub Pages will automatically issue an SSL certificate once it sees the domain
3. Verify in repo Settings > Pages — it should show "Your site is live at https://oakhem.com"

## GitHub Pages Info

- Repo: https://github.com/oak8513/ycr-site
- Default Pages URL (works now): https://oak8513.github.io/ycr-site/
- Custom domain (after DNS): https://oakhem.com

## File Structure

```
ycr-site/
  CNAME              <- tells GitHub Pages to serve on oakhem.com
  index.html         <- homepage
  services.html
  about.html
  contact.html
  blog/
    index.html       <- blog listing
    YYYY-MM-DD-slug.html  <- auto-generated posts
  sitemap.xml
  robots.txt
```
