import os
import re
from console_logging.console import Console
console = Console()
import datetime
import time


def make_sitemap(urls):
    entries = []
    timestamp = datetime.datetime.fromtimestamp(time.time())
    gmtoffset = timestamp.astimezone().utcoffset().seconds
    timestamp = "{year}-{month}-{day}T{hour}:{minute}:{second}+{timeshift}".format(
        year=timestamp.year, month=timestamp.month, day=timestamp.day,
        hour=timestamp.hour, minute=timestamp.minute, second=timestamp.second,
        timeshift='%02d:%02d' % (gmtoffset // 3600, (gmtoffset % 3600) // 60)
    )
#Fix this region widespread mess. [Figure out what the fuck sitemap.XML is.]
    for url in urls:
        sitemap_entry = "<url>\n<loc>{url}</loc>\n<lastmod>{timestamp}</lastmod>\n<priority>0.8</priority></url>".format(
            url='http://masq.gq%s' % url, timestamp=timestamp)
        entries.append(sitemap_entry)
    sitemap_xml = '''<?xml version="1.0" encoding="UTF-8"?>
                        <urlset
                            xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
                            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                            xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
                                    http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
                        <!-- created with Free Online Sitemap Generator www.xml-sitemaps.com -->

                        <url>
                        <loc>http://masq.gq/</loc>
                        <lastmod>2017-11-19T19:27:39+00:00</lastmod>
                        <priority>1.00</priority>
                        </url>
                        %s
                        </urlset>''' % '\n'.join(entries)
    with open('sitemap.xml', 'w') as f:
        f.write(sitemap_xml)
    return

#End on this region [Fix lines 18-40]

def parse_blog(blogdat: list):
    blog = dict()
    blog['title'] = blogdat[0][:-1]
    blog['excerpt'] = blogdat[3]

    def parse_timestamp(timestamp: str):
        date, time = timestamp.split(' ')
        month, day, year = date.split('/')
        hours, minutes = time.split(':')
        date = dict()
        time = dict()
        date['m'] = month
        date['d'] = day
        date['y'] = year
        time['h'] = hours
        time['m'] = minutes
        return {'date': date, 'time': time}
    blog['timestamp'] = parse_timestamp(blogdat[1][:-1])
    blog['tags'] = re.sub(' ', '', blogdat[2][:-1]).lower().split(',')
    blog['nsfw'] = 'nsfw' in blog['tags']
    blog['body'] = [line.replace('\n', '') for line in blogdat[5:]]
    return blog


blog_posts = []


def render_blog(blog: dict):
    title = '<h1>%s <small>%s</small></h1>' % (
        blog['title'], ('(NSFW)' if blog['nsfw'] else ''))
    date = blog['timestamp']['date']
    time = blog['timestamp']['time']
    timestamp = '%s/%s/%s || %s:%s' % (date['m'],
                                       date['d'],
                                       date['y'],
                                       time['h'],
                                       time['m'])

    def render_body(body: list):
        body_ = []
        for line in body:
            if '-' in line and len(line.replace('-', '')) == 0:
                body_.append('<hr>')
            elif line == '~':
                body_.append('<hr>')  # TODO: add tilda
            elif len(line) > 0 and len(re.sub('(\[).+(\])(\().+(\))', '', line)) == 0:
                alt_text = line[1:line.rfind(']')]
                link = line[line.find('(') + 1:-1]
                body_.append('<img src="{link}" alt="{alt}">'.format(
                    link=link,
                    alt=alt_text))
            else:
                while line.count('*') > 1:
                    print(line)
                    occ1 = line.find('*')
                    occ2 = occ1 + line[occ1 + 1:].find('*') + 1
                    line = '%s<b>%s</b>%s' % (line[:occ1],
                                              line[occ1 + 1:occ2], line[occ2 + 1:])
                while line.count('_') > 1:
                    print(line)
                    occ1 = line.find('_')
                    occ2 = occ1 + line[occ1 + 1:].find('_') + 1
                    line = '%s<i>%s</i>%s' % (line[:occ1],
                                              line[occ1 + 1:occ2], line[occ2 + 1:])
                while line.count('~') > 1:
                    print(line)
                    occ1 = line.find('~')
                    occ2 = occ1 + line[occ1 + 1:].find('~') + 1
                    line = '%s<s>%s</s>%s' % (line[:occ1],
                                              line[occ1 + 1:occ2], line[occ2 + 1:])
                body_.append('<p>%s</p>' % line)
        return '\n'.join(body_)
    body = render_body(blog['body'])
    blog_posts.append({
        'title': blog['title'],
        'date': date, 'time': time,
        'excerpt': blog['excerpt']
    })
    #Modify Analytics Tag lines 123-132
    analytics_tag = '''<!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-126638765-1"></script>
        <script>
             window.dataLayer = window.dataLayer || [];
             function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'UA-126638765-1');
        </script>
                    '''
    #Modify Analytics Tag lines 123-132
    return '''<!DOCTYPE html>
                <html>
                {head}
                <body>
                    <div class="container">
                    <h1>{title}</h1>
                    <a href="../" style="
                        font-weight: 800;
                        text-decoration: unset;
                    ">&lt; Back to Blog</a>
                    <h6>Tagged: {tags}
                    <span>{timestamp}</span></h6>
                    <p>{body}</p><br><br><br><br><br>
                    </div>
                </body>
                </html>'''.format(head='<head>\n{analytics}\n<link rel="shortcut icon" type="image/x-icon" href="favicon.ico">\n<link rel="apple-touch-icon" sizes="57x57" href="/icons/apple-icon-57x57.png">\n<link rel="apple-touch-icon" sizes="60x60" href="/icons/apple-icon-60x60.png">\n<link rel="apple-touch-icon" sizes="72x72" href="/icons/apple-icon-72x72.png">\n<link rel="apple-touch-icon" sizes="76x76" href="/icons/apple-icon-76x76.png">\n<link rel="apple-touch-icon" sizes="114x114" href="/icons/apple-icon-114x114.png">\n<link rel="apple-touch-icon" sizes="120x120" href="/icons/apple-icon-120x120.png">\n<link rel="apple-touch-icon" sizes="144x144" href="/icons/apple-icon-144x144.png">\n<link rel="apple-touch-icon" sizes="152x152" href="/icons/apple-icon-152x152.png">\n<link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-icon-180x180.png">\n<link rel="icon" type="image/png" sizes="192x192"  href="/icons/android-icon-192x192.png">\n<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32x32.png">\n<link rel="icon" type="image/png" sizes="96x96" href="/icons/favicon-96x96.png">\n<link rel="icon" type="image/png" sizes="16x16" href="/icons/favicon-16x16.png">\n<link rel="manifest" href="/manifest.json">\n<meta name="msapplication-TileColor" content="#ffffff">\n<meta name="msapplication-TileImage" content="/icons/ms-icon-144x144.png">\n<meta http-equiv="cache-control" content="max-age=0" />\n<meta http-equiv="cache-control" content="no-cache" />\n<meta http-equiv="expires" content="0" />\n<meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />\n<meta http-equiv="pragma" content="no-cache" />\n<meta name="google-site-verification" content="QemKi946DJdn-qh6dI_g6UooSulgQgNMAe58ns35Q9Y"/>\n<title>CodeX</title>\n<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">\n<link rel="stylesheet" href="../css/blog.css">\n<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script></head>'.format(analytics=analytics_tag),
                                  title=title, timestamp=timestamp,
                                  body=body, tags=blog['tags'])


try:
    os.makedirs('./blog')
except:
    pass

for file in os.listdir('./blogs'):
    ext = file.split('.')[-1]
    if ext == 'blog':
        blog_id = file.split('.')[0]
        with open('./blogs/%s' % file, 'r') as blog_def:
            parsed_blog = parse_blog(blog_def.readlines())
            blog_html = render_blog(parsed_blog)
            with open('./blog/%s.html' % blog_id, 'w') as blog:
                blog.write(blog_html)
            blog_posts[-1]['url'] = '/blog/%s.html' % blog_id
        console.info("Wrote blog id::%s" % blog_id)
    blog_posts.sort(key=lambda blog_post: int(
        blog_post['date']['m']) * 32 * 3600 + int(blog_post['date']['d']) * 3600 + int(blog_post['date']['y']) * 367 * 3600 + int(blog_post['time']['h']) * 60 + int(blog_post['time']['m'][:2]))
    blog_posts.reverse()
    index = []
    for blog_post in blog_posts:
        index.append(
            '''<div class="col-md-6 item">
                   <div class="item-in">
                       <h4>{title}</h4>
                       <div class="seperator"></div>
                       <p>{date}: {excerpt}</p>
                        <a href="{url}">Read More<i class="fa fa-long-arrow-right"></i></a>
                    </div>
               </div>'''.format(
                title=blog_post['title'],
                date="%s/%s/%s" % (blog_post['date']['m'],
                                   blog_post['date']['d'],
                                   blog_post['date']['y']),
                excerpt=blog_post['excerpt'],
                url=blog_post['url'][:-5]
            ))
        console.info("Created index entry for post \"%s\"" %
                     blog_post['title'])
    rows = []
    while len(index) > 0:
        posts = index[:2]
        index = index[2:]
        rows.append('<div class="row">%s</div>' % '\n'.join(posts))
    console.info("Created rows.")
    index_html = '''<!DOCTYPE html>
                    <html>

                    <head>
                        <!-- Global site tag (gtag.js) - Google Analytics -->
                        <script async src="https://www.googletagmanager.com/gtag/js?id=UA-126638765-1"></script>
                        <script>
                        window.dataLayer = window.dataLayer || [];
                        function gtag(){dataLayer.push(arguments);}
                        gtag('js', new Date());

                        gtag('config', 'UA-126638765-1');
                        </script>
                        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
                         <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
                        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
                        <link rel="manifest" href="/site.webmanifest">
                        <meta name = "keywords" content = "CUNY, SUNY, COMMONAPP, FAFSA, TAP" />                        
                        <title>SSCWEB.</title>
                         <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">
                        <link rel="stylesheet" prefetch href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
                        <link rel="stylesheet" href="css/style.css">
                        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">
                        <link rel='stylesheet prefetch' href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css'>
                         <link rel="stylesheet" href="css/style.css">
                    </head>

                    <body>
                        <section class="title container">
                            <div class="row">
                                <div class="col-md-12">
                                    <h1>Code<fade>X</fade> Blog</h1>
                                    <div class="seperator"></div>
                                    <p style="padding-bottom:50px;"></p>
                                </div>
                            </div>
                        </section>

                        <!-- Start Blog Layout -->
                        <div class="container">
                            %s
                        </div>

                    </body>

                    </html>''' % '\n'.join(rows)
    with open('index.html', 'w') as index_file:
        index_file.write(index_html)
    console.info("Wrote index HTML.")
    make_sitemap([blog_post['url'] for blog_post in blog_posts])
console.success("Finished blog iteration.")
