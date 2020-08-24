import builtwith
import whois
import re
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import ssl
import json

ssl._create_default_https_context = ssl._create_unverified_context

class Page:
    def __init__(self, site, chave):
        self.site = site
        self.chave = chave

    def get_result(self):
        url1 = "https://www.bemol.com.br/pesquisa?t=" + self.chave.replace(" ", "+")
        url2 = "https://www.ramsons.com.br/pesquisa?t=" + self.chave.replace(" ", "+")
        url3 = "https://truedata.com.br/b/" + self.chave.replace(" ", "%20")
        url4 = "https://fotonascimento.com.br/?s=" + self.chave.replace(" ", "%20") + "&product_cat=0&post_type=product"
        url5 = "https://www.infostore.com.br/catalogsearch/result/?q=" + self.chave.replace(" ", "+")

        urls = list()
        urls.append(url1)
        urls.append(url2)
        urls.append(url3)
        urls.append(url4)
        urls.append(url5)

        jobs = []
        for ur in urls:
            if self.site in "all":
                jobs.append(self.scrape(ur))
            else:
                if ur.find(self.site) > 0:
                    jobs.append(self.scrape(ur))
                    break

        return json.dumps(jobs)

    def scrape(self, url):
        try:
            req = Request(url, headers={'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"})
            html = urlopen(req)
            bsObj = BeautifulSoup(html.read(), "html.parser")
            job = {}

            if url.find("bemol") > 0:
                job["bemol"] = self.read_bemol(bsObj)
            elif url.find("ramsons") > 0:
                job["ramsons"] = self.read_ramsons(bsObj)
            elif url.find("truedata") > 0:
                job["truedata"] = self.read_true_data(bsObj)
            elif url.find("fotonascimento") > 0:
                job["fotonascimento"] = self.read_foto_nascimento(bsObj)
            elif url.find("infostore") > 0:
                job["infostore"] = self.read_info_store(bsObj)

            return job
        except URLError as erro:
            print(f"Error HTTP: {erro}")
        except HTTPError as erro:
            print(f"Error URL: {erro}")

    def read_bemol(self, bsObj):
        jobs = []
        job = {}

        skus = bsObj.findAll("div", {"class": "wd-product-notifywhenavailable wd-widget wd-widget-js"})
        if len(skus) > 0:
            for sku in skus:
                url = sku.findAll("img", {"class": "photo"})
                name = sku.findAll("div", {"class": "product-name"})
                preco = sku.findAll("div", {"class": "wd-product-price-description wd-widget wd-widget-js"})

                job = {}
                job['name'] = name[0].getText()
                job['image'] = url[0]['src']
                job['brand'] = 'sb'
                job['category'] = 'sc'
                job['link'] = bsObj.findAll("link", {"rel": "canonical"})[0]['href']
                job['preco'] = re.findall('(?:R\$\s)([0-9\.\,]+)', preco[0].getText())[0]
                jobs.append(job)
        else:
            detalhes = bsObj.findAll("div", {"class": "wd-product-line"})
            for detalhe in detalhes:
                preco = re.findall('(?:R\$\s)([0-9\.\,]+)', detalhe.getText())

                job = {}
                job['name'] = detalhe["data-name"]
                job['image'] = detalhe.findAll("img", {"class": "lazyload current-img no-effect"})[0]['data-src']
                job['brand'] = detalhe["data-brand"]
                job['category'] = detalhe["data-category"]
                job['link'] = "https://www.bemol.com/br" + detalhe.findAll("a", {"class": "maisDetalhes"})[0]['href']
                job['preco'] = preco[0]
                jobs.append(job)

        return jobs

    def read_ramsons(self, bsObj):
        jobs = []
        job = {}

        skus = bsObj.findAll("div", {"class": "wd-product-notifywhenavailable wd-widget wd-widget-js"})
        if len(skus) > 0:
            for sku in skus:
                url = sku.findAll("img", {"class": "photo"})
                name = sku.findAll("div", {"class": "product-name"})
                preco = sku.findAll("div", {"class": "wd-product-price-description wd-widget wd-widget-js"})

                job = {}
                job['name'] = name[0].getText()
                job['image'] = url[0]['src']
                job['brand'] = 'sb'
                job['category'] = 'sc'
                job['link'] = bsObj.findAll("link", {"rel": "canonical"})[0]['href']
                job['preco'] = re.findall('(?:R\$\s)([0-9\.\,]+)', preco[0].getText())[0]
                jobs.append(job)
        else:
            detalhes = bsObj.findAll("div", {"class": "wd-product-line"})
            for detalhe in detalhes:
                preco = re.findall('(?:R\$\s)([0-9\.\,]+)', detalhe.getText())

                job = {}
                job['name'] = detalhe["data-name"]
                job['image'] = detalhe.findAll("img", {"class": "lazyload current-img fade animated"})[0]['data-src']
                job['brand'] = detalhe["data-brand"]
                job['category'] = detalhe["data-category"]
                job['link'] = "https://www.ramsons.com.br" + detalhe.findAll("h3", {"class": "name"})[0].findAll("a")[0]['href']
                job['preco'] = preco[0]
                jobs.append(job)

        return jobs

    def read_true_data(self, bsObj):
        jobs = []
        job = {}

        detalhes = bsObj.findAll("div", {"class": "product-result showcase__item"})
        for detalhe in detalhes:
            job = {}
            job['name'] = detalhe.findAll("h3", {"class": "showcase-product__title"})[0].getText().strip()
            job['image'] = detalhe.findAll("img", {"class": "showcase-product__image lazy"})[0]['data-original']
            job['brand'] = detalhe.findAll("meta", {"itemprop": "brand"})[0]["content"]
            job['category'] = ""
            job['link'] = "https://truedata.com.br" + detalhe.findAll("a", {"class": "showcase-product__link showcase-product__link_image"})[0]['href']
            job['preco'] = detalhe.findAll("strong", {"class": "showcase-prices__price color-first"})[0].getText().strip().replace("R$ ", "")
            jobs.append(job)

        return jobs

    def read_foto_nascimento(self, bsObj):
        jobs = []
        job = {}

        detalhes = bsObj.findAll("div", {"class": "product-outer product-item__outer"})
        for detalhe in detalhes:
            preco = detalhe.findAll("span", {"class": "woocommerce-Price-amount amount"})

            job = {}
            job['name'] = detalhe.findAll("h2", {"class": "woocommerce-loop-product__title"})[0].getText().strip()
            job['image'] = detalhe.findAll("img", {"class": "attachment-woocommerce_thumbnail size-woocommerce_thumbnail"})[0]['src']
            job['brand'] = detalhe.findAll("a", {"rel": "tag"})[0].getText().strip()
            job['category'] = "sc"
            job['link'] = detalhe.findAll("a", {"class": "woocommerce-LoopProduct-link woocommerce-loop-product__link"})[0]['href']
            job['preco'] = re.findall('.*', preco[0].getText())[0].replace("R$", "")
            jobs.append(job)

        return jobs

    def read_info_store(self, bsObj):
        jobs = []
        job = {}

        detalhes = bsObj.findAll("ol", {"class": "products list items product-items"})
        if len(detalhes) > 0:
            listas = detalhes[0].findAll("li", {"class": "item product product-item"})

            for lista in listas:
                nome = lista.findAll("a", {"class": "product-item-link"})[0].getText().strip()
                image = lista.findAll("img", {"class": "product-image-photo"})[0]['src']
                link = lista.findAll("a", {"class": "product-item-link"})[0]['href']
                preco = lista.findAll("span", {"class": "price"})

                job = {}
                if len(preco) > 0:
                    job['name'] = nome
                    job['image'] = image
                    job['brand'] = 'sb'
                    job['category'] = "sc"
                    job['link'] = link
                    job['preco'] = preco[0].getText().replace("R$", "")
                    jobs.append(job)

        return jobs
