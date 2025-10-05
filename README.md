# Wordpress Plugin Scanner
HackingCamp 27, PoC Security ( CTF Player to Hacker : 선택과 집중 )

# WordPress Vulnerability Scan Results
Below are the identified CVEs from the scan :
```
CVE-2023-29385, CVE-2023-29441, CVE-2023-30471, CVE-2023-30472, CVE-2023-30487,
CVE-2023-30493, CVE-2023-30499, CVE-2023-30779, CVE-2023-30871, CVE-2023-30473,
CVE-2023-31071, CVE-2023-30868, CVE-2023-30877, CVE-2023-31230, CVE-2023-31233,
CVE-2023-32122, CVE-2023-32740, CVE-2023-33313, CVE-2023-33927, CVE-2023-34026,
CVE-2023-34185, CVE-2023-34181, CVE-2023-34177, CVE-2023-34174, CVE-2023-34371,
CVE-2023-34372, CVE-2023-35047, CVE-2023-35043, CVE-2023-35098, CVE-2023-35778,
CVE-2023-35780, CVE-2023-35877, CVE-2023-35878, CVE-2023-36508, CVE-2023-35878,
CVE-2023-36692, CVE-2023-36693, CVE-2023-37977, CVE-2023-37981, CVE-2023-40215,
CVE-2023-39992, CVE-2023-40663, CVE-2023-41667, CVE-2023-41668, CVE-2023-41669,
CVE-2023-45003, CVE-2023-45064, CVE-2023-45761, CVE-2023-45770, CVE-2023-45771,
CVE-2023-46071, CVE-2023-46074, CVE-2023-46075, CVE-2023-46076, CVE-2023-46088,
CVE-2023-46089, CVE-2023-46090, CVE-2023-46091, CVE-2023-46092, CVE-2023-46093,
CVE-2023-46191, CVE-2023-46192, CVE-2023-46193
```

# downloader.py

## Usage
```bash
# 특정 키워드로 검색
python3 downloader.py --keyword security seo backup

# 공백 포함 키워드
python3 downloader.py --keyword "contact form" "payment gateway" woocommerce

# 짧은 플래그 사용
python3 downloader.py -k elementor gutenberg wordpress

# 기본 키워드 사용 (플래그 없이)
python3 downloader.py
```


# Setting up WordPress with Docker

## Basic WordPress Docker Setup
```bash
# 1. Pull required images
docker pull mysql:5.7
docker pull wordpress

# 2. Create MySQL container
docker run -d --name mysql_db \
  -e MYSQL_ROOT_PASSWORD=toor \
  -e MYSQL_DATABASE=wpdb \
  -e MYSQL_USER=wp \
  -e MYSQL_PASSWORD=wppass \
  -v mysql:/var/lib/mysql \
  mysql:5.7

# 3. Create WordPress container
docker run -d --name wp \
  -p 8080:80 \
  --link mysql_db:wpdb \
  -e WORDPRESS_DB_HOST=wpdb \
  -e WORDPRESS_DB_USER=wp \
  -e WORDPRESS_DB_PASSWORD=wppass \
  -e WORDPRESS_DB_NAME=wpdb \
  -v wp:/var/www/html \
  wordpress
```

## One-Line Command (Apple Silicon/M1/M2)
```bash
docker pull mysql:5.7 --platform linux/amd64; \
docker pull wordpress --platform linux/amd64; \
docker run -d --name mysql_db \
  -e MYSQL_ROOT_PASSWORD=toor \
  -e MYSQL_DATABASE=wpdb \
  -e MYSQL_USER=wp \
  -e MYSQL_PASSWORD=wppass \
  -v mysql:/var/lib/mysql mysql:5.7; \
docker run -d --name wp \
  -p 8888:80 \
  --link mysql_db:wpdb \
  -e WORDPRESS_DB_HOST=wpdb \
  -e WORDPRESS_DB_USER=wp \
  -e WORDPRESS_DB_PASSWORD=wppass \
  -e WORDPRESS_DB_NAME=wpdb \
  -v wp:/var/www/html wordpress
```

**Note:**
- External Port: 8888
- Internal Port: 80
- MySQL Password: wppass

## Accessing Container Shells
```bash
# Access WordPress container
docker exec -it wp bash

# Access MySQL container
docker exec -it mysql_db bash
```

## Accessing MySQL in Container
```bash
# 1. First access the MySQL container
docker exec -it mysql_db bash

# 2. Then connect to MySQL
mysql -u wp -p
# Enter password when prompted: wppass

# 3. Basic MySQL commands
mysql> show databases;
# Should display 'wpdb' and 'information_schema'

# 4. Exit MySQL and container
mysql> exit
root@container:/# exit
```
