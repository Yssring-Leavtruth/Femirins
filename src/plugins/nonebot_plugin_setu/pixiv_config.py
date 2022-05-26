
import re
from ..nonebot_plugin_utlie import config

class PixivConfig:

    headers = {
        'referer': 'https://www.pixiv.net/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'cookie': 'first_visit_datetime_pc=2021-06-22+19%3A49%3A43; p_ab_id=3; p_ab_id_2=9; p_ab_d_id=1783321249; yuid_b=JwdUKFQ; _gcl_au=1.1.905054339.1624358985; __utmz=235335808.1624358986.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _ga=GA1.2.774961664.1624358986; PHPSESSID=23370059_pdqVIG3xt5KRE19V5rE83qhzjt1c8qLf; c_type=24; privacy_policy_agreement=0; privacy_policy_notification=0; a_type=0; b_type=1; ki_r=; ki_u=a3c4cebb-79b7-9500-eb9c-58aa; login_ever=yes; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=23370059=1^9=p_ab_id=3=1^10=p_ab_id_2=9=1^11=lang=zh=1; ki_s=214908%3A0.0.0.0.2%3B214994%3A0.0.0.0.2%3B215190%3A0.0.0.0.2%3B216591%3A1.0.0.1.1%3B217356%3A0.0.0.0.2; _im_vid=01FAW4X6MWDY8AT1GMMYJV6S7H; __gads=ID=cb5cf37ffd5abaf4:T=1627572288:S=ALNI_MYeEIUM1dTjJqBoRDpuViy-iZ7NwQ; cto_bundle=lmLWgl8lMkYwTm90SVhNVU5EbWlQWm1QRGx2JTJGUnBDdDhrUHNnSlVDbkhCVnZFajZSRnNQa2pMdlhGSGNQaEZLd2FwbmhPcjFhUEJ3bmxhYktUUUdlamFrblFMZUxEYk4zJTJCMFNkQ2ducG5FeGtPdXZOdEtpTTZadHM5UWM2Rkg2bWxMZm5OdldzZFBQS0RhTXRKZDNLbmtoU3h3YXclM0QlM0Q; ki_t=1624359421613%3B1627572145093%3B1627574219382%3B8%3B26; __utmc=235335808; __utma=235335808.774961664.1624358986.1628048286.1628055692.31; _gid=GA1.2.2135953565.1628056037; tag_view_ranking=_EOd7bsGyl~BSlt10mdnm~q303ip6Ui5~0xsDLqCEW6~ziiAzr_h04~Lt-oEicbBr~OUF2gvwPef~RTJMXD26Ak~MnGbHeuS94~J5hwvO5aFP~tgP8r-gOe_~zyKU3Q5L4C~GvNjYYlm80~BU9SQkS-zU~y8GNntYHsi~VRuBtwFc6O~DlTwYHcEzf~hW_oUTwHGx~bvp7fCUKNH~KOnmT1ndWG~pzZvureUki~HY55MqmzzQ~Ie2c51_4Sp~v0NUUDccsO~kGYw4gQ11Z~jk9IzfjZ6n~q3eUobDMJW~azESOjmQSV~m47KFuLUuf~BrsBIfWNi7~lH5YZxnbfC~-StjcwdYwv~HLWLeyYOUF~pj2CPHCQJt~wKl4cqK7Gl~Bd2L9ZBE8q~5oPIfUbtd6~QaiOjmwQnI~IJkCuj9g6o~KN7uxuR89w~gooMLQqB9a~4Q1GaIiU6i~NpsIVvS-GF~I6pg0OTBFE~MbwovAGX1h~d3xXMR1RDK~txZ9z5ByU7~QniSV1XRdS~5BhtaeNUYC~hRUnVPuHhQ~2acjSVohem~jH0uD88V6F~I-1xQGtn3G~5Z-Ks7Elpa~TqiZfKmSCg~ZnmOm5LdC3~WuRP3NHCdl~mPFmmA9wY_~NW99fuIGG8~EZQqoW9r8g~dJgU3VsQmO~R3lr4__Kr8~gpglyfLkWs~PaXCbritTZ~1pqyuWNrAr~NT6HjMvlFJ~fom2ZioKkS~YD-NOMU9Pq~i_dZaon0j6~XR2TkWmDsz~_LAZq-jG_L~vJzu26Ndou~i83OPEGrYw~7YjK_c_EhV~r01unnQL0a~CrFcrMFJzz~PsDkAv1zHU~D0nMcn6oGk~4ZEPYJhfGu~K8esoIs2eW~fg8EOt4owo~AauDVIJZFs~u8McsBs7WV~_sjpLQz14H~bopfpc8En6~0Sds1vVNKR~_pwIgrV8TB~bqRR7rH23v~UR3UZdHtim~mHukPa9Swj~bcAbumoPKA~dg_40nEhSE~Ged1jLxcdL~nUBVELKKm6~VLPolKc5hy~nwiQZCmIlX~cryvQ5p2Tx~J3A2yiE7Cn~owkewPBYPl~mqf4KYn6Dx; _im_uid.3929=; __cf_bm=c4eb2dbfcc7fcd2c957958405b26e1d74436e25a-1628062809-1800-AVCMWYARolNFSH8r6vU/H1Wo6MY0SWGLRH1br8Hr+c33Wa+aU5dJNG5tYELJyu4Q1prf3/XcFWryZLHYjEYn50Bbl4F+lmiKO4ywKho92dghqa02GHW7oStLkRjp3ZBGcLCH06HLKERAvv3z925zprTuvzTgdZBmBKQBcUhy5GAcyfhd+GSUY85jmZ6VI+Wf6Q==; __utmt=1; __utmb=235335808.89.10.1628055692'
    }

    image_url = {
        'original': 'https://i.pixiv.cat/img-original/img/%s.jpg',
        'regular': 'https://i.pixiv.cat/img-master/img/%s_master1200.jpg',
        'small': 'https://i.pixiv.cat/c/540x540_70/img-master/img/%s_master1200.jpg',
        'thumb': 'https://i.pixiv.cat/c/250x250_80_a2/img-master/img/%s_square1200.jpg'
    }

    size = config.setu_size

    @classmethod
    def get_image_url(cls, url: str):

        ite = re.finditer(r'.*/img/(.*_p\d).*', url)
        img = ite.__next__().group(1)

        return cls.image_url[cls.size] % img