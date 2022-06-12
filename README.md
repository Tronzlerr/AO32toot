### 基于Feed2toot的AO3 tag订阅脚本

本质是对Feed2toot进行了一些修改，使它能够更好地解析AO3提供的rss feed，并调整发布嘟文时的格式。

（对不起我太菜了……写解析函数的时候只针对AO3的rss订阅格式，所以这个脚本目前订阅不了其他rss）

脚本安装、配置及运行方法均参见Feed2toot文档：https://feed2toot.readthedocs.io/en/latest/use.html

关于配置文件中``[rss]`` section支持解析四个部分，``{title}`` - 标题，``{published}`` - 发布时间，``{link}`` - 链接，``{summary}`` - 摘要及相关信息，以下为单tag订阅示例。如需订阅多个tag请在[rss] section中使用``uri_list``参数替代``uri``。

```
[rss]
uri=https://archiveofourown.org/tags/217263/feed.atom
toot={title} {published} {link} {summary} 
toot_max_len=1000
```

``[mastodon]`` section中新增参数``use_cw``，选项为Y或N，用于选择发布嘟文时是否折叠（默认折叠）。

```
[mastodon]
instance_url=https://mastodon.social
user_credentials=feed2toot_usercred.txt
client_credentials=feed2toot_clientcred.txt
; Default visibility is public, but you can override it:
toot_visibility=unlisted
use_cw=Y
```

P.S. AO3的rss订阅并不会包括仅登陆可见的文章，也不含有已经发布的文章的章节更新消息。

P.P.S 如果用cron定时运行脚本，配置文件内部的所有路径都需要写绝对路径。

---

### ↓ 原始项目介绍 ↓

---

### Feed2toot

Feed2toot automatically parses rss feeds, identifies new posts and posts them on the [Mastodon](https://mastodon.social) social network.
For the full documentation, [read it online](https://feed2toot.readthedocs.io/en/latest/).

If you would like, you can [support the development of this project on Liberapay](https://liberapay.com/carlchenet/).
Alternatively you can donate cryptocurrencies:

- BTC: 1AW12Zw93rx4NzWn5evcG7RNNEM2RSLmAC
- XMR: 43GGv8KzVhxehv832FWPTF7FSVuWjuBarFd17QP163uxMaFyoqwmDf1aiRtS5jWgCiRsi73yqedNJJ6V1La2joznKHGAhDi

### Quick Install

* Install Feed2toot from PyPI

        # pip3 install feed2toot

* Install Feed2toot from sources
  *(see the installation guide for full details)
  [Installation Guide](http://feed2toot.readthedocs.io/en/latest/install.html)*


        # tar zxvf feed2toot-0.17.tar.gz
        # cd feed2toot
        # python3 setup.py install
        # # or
        # python3 setup.py install --install-scripts=/usr/bin

### Create the authorization for the Feed2toot app

* Just launch the following command::

        $ register_feed2toot_app

### Use Feed2toot

* Create or modify feed2toot.ini file in order to configure feed2toot:

        [mastodon]
        instance_url=https://mastodon.social
        user_credentials=feed2toot_usercred.txt
        client_credentials=feed2toot_clientcred.txt
        ; Default visibility is public, but you can override it:
        ; toot_visibility=unlisted
        
        [cache]
        cachefile=cache.db
        
        [rss]
        uri=https://www.journalduhacker.net/rss
        toot={title} {link}
        
        [hashtaglist]
        several_words_hashtags_list=hashtags.txt

* Launch Feed2toot

        $ feed2toot -c /path/to/feed2toot.ini

### Authors

* Carl Chenet <carl.chenet@ohmytux.com>
* Antoine Beaupré <anarcat@debian.org>
* First developed by Todd Eddy

### License

This software comes under the terms of the GPLv3+. Previously under MIT license. See the LICENSE file for the complete text of the license.
