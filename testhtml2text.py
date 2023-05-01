#!/usr/bin/python3
import html2text

h = html2text.HTML2Text()
h.ignore_links = True
h.ignore_images = True
h.images_to_alt = True
h.ignore_tables = True
h.ignore_emphasis = True

content = '''<div class="postion-relative js-jvcode-sticky-postion">
<p class="jvcode-sticky-position"><a class="btn-call-to-action shop js-tracking-widget" data-tracking-category="affiliateclick-content_cta" data-tracking-click-action-name="boulanger" data-tracking-events="click" data-tracking-label="https://fnty.co/c/r-bnQqQmqv" href="https://fnty.co/c/r-bnQqQmqv" rel="sponsored" target="_blank"><span class="nav-icon-shop"></span><span class="ellipsed-text">Acheter la U8HQ à 799 € chez Boulanger</span></a></p><h2 class="h2-default-jv" id="hisense-u8hq-une-tv-4k-mini-led-qled-polyvalente-et-parfaite-pour-ps5">Hisense U8HQ : Une TV 4K Mini-LED QLED polyvalente et parfaite pour PS5</h2><p>À la recherche d'une très bonne TV 4K pour votre PS5 ou votre Xbox Series ? La Hisense U8HQ est un excellent choix pour vous grâce à son très bon rapport qualité prix. Sur ses caractéristiques, elle est parfaitement au point et propose ainsi la 4K UHD à 120 images par seconde grâce à son taux de rafraîchissement de 120 Hz et à ses 2 ports HDMI 2.1. Ces derniers sont d'ailleurs compatibles avec VRR, pour Variable Refresh Rate. Cela permet à votre téléviseur de se synchroniser avec votre console afin que la fréquence de rafraîchissement soit égale au nombre d'images envoyé. L'ALLM, pour Auto Low Latency Mode est aussi présent et fait automatiquement basculer votre TV en mode jeu, réduisant ainsi la latence de cette dernière. Enfin, le FreeSync est présent et permettra une expérience fluide sans saccades et déchirures d'image même dans les parties les plus endiablées. < /p > <p > Au niveau de la dalle en elle même, nous sommes sur une taille de 55 pouces. Elle est dotée de la technologie Mini-LED, qui permet d'avoir de très bons contrastes tout en gardant une très bonne luminosité. Cette technologie a aussi l'avantage de ne pas avoir de problèmes de marquages à l'opposé de l'OLED. De plus, elle dispose de la technologie QLED qui vient améliorer l'image grâce à des Quantum Dots.</p><p>La U8HQ pourra vous permettre de regarder de nombreux contenus HDR, vu qu'elle est compatible avec Dolby Vision, mais aussi HDR10, HDR10 + et HLG. Son système sonore 2.1.2 canaux est très efficace et dispose tout de même d'une puissance de 70 Watts ! Il supporte les formats Dolby Atmos et DTS : X et offre ainsi un son puissant et immersif. </p><ul class="liste-default-jv"><li>Bonus intéressant : le mode Filmmaker est présent sur ce téléviseur et vous permettra de regarder vos films et séries de la manière la plus fidèle à la volonté des réalisateurs. </li></ul><p>Pour finir, comme une majorité des TV sorties récemment c'est une SmartTV. Elle a donc accès à un grand nombre d'applications comme Youtube, Netflix, Prime Vidéo ou Disney+. Elle peut aussi être contrôlée à la voix grâce à des assistants vocaux comme Alexa et Google Assistant. </p></div>'''

print(h.handle(content))
