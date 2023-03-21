import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd

service=Service(executable_path=ChromeDriverManager().install())

class social_media():
    def __init__(self):
        self.driver=webdriver.Chrome(service=service)

        self.platform={}

        self.platform['instagram']={
            'main_url':r'https://www.instagram.com/',
            'login_url':r'https://www.instagram.com/',
            'userbox':['name','username'],
            'passbox':['name','password'],
            'landing_page':['class','cmbtv'],
            'profile_insight':{'class':'_aacl _aacp _aacu _aacx _aad6 _aade'},
            'posts-pages':['class','_aa-i'],
            'posts':{'class':'_aabd _aa8k _aanf'},
            'insight':['xpath','/html/body/div[1]/div/div[1]/div/div[1]/div/div/div/div[1]/div[1]/section/main/div[1]/div[1]/article/div/div[2]/div/div[2]/section[1]/div/section/button'],
            'post_insight':{'data-bloks-name':'bk.components.Text'},
            'categories':['likes','comentarios','compartidos']#,'interacciones']
        }

        self.platform['facebook']={
            'main_url':r'https://es-la.facebook.com',
            'login_url':r'https://es-la.facebook.com',
            'userbox':['name','email'],
            'passbox':['name','pass'],
            'landing_page':['class','j83agx80 cbu4d94t l9j0dhe7 iiifoker bp4zxj6n']
        }

        self.platform['twitter']={
            'main_url':r'https://twitter.com/',
            'login_url':r'https://twitter.com/i/flow/login',
            'userbox':['name','text'],
            'passbox':['name','password'],
            'landing_page':['xpath','/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[7]/div'],
            'profile_insight':{'class':"css-4rbku5 css-18t94o4 css-901oao r-18jsvk2 r-1loqt21 r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0"},
            'posts':{'class':'css-1dbjc4n r-18u37iz r-1h0z5md'},
            'posts-pages':['xpath','/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/div[1]/div/div/div/article/div/div/div/div[2]/div[2]/div[2]/div[2]/div/div[5]/a/div'],
            'insight':['xpath','/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[2]/div[1]/div[1]/div'],
            'post_insight':{'class':"css-901oao r-18jsvk2 r-37j5jr r-a023e6 r-b88u0q r-rjixqe r-bcqeeo r-q4m81j r-qvutc0"},
            'categories':['likes','compartidos','comentarios']#,'impresiones','interacciones']
        }

        self.info={'post':[],'likes':[],'compartidos':[],'comentarios':[]}#,'interacciones':[],'impresiones':[]}

    def __wait(self,element,element_identifier=''):
        '''
        function design for explicit waiting on UI objects
        element: type of element [name,id,link_text,css....]
        element identifier: the name or class assigned to the element
        '''
        # # print('received element:',element)
        if isinstance(element,list):
            element_identifier=element[1]
            element=element[0]
        elif isinstance(element,dict):
            for a,b in element.items():
                element_identifier=b
                element=a

        try:#explicit waits
            if element.lower()=='name':
                #primero intentar con nombre
                a=WebDriverWait(self.driver,5).until(ec.presence_of_element_located((By.NAME,element_identifier)))
            elif element.lower()=='id':
                #intenter con ID
                a=WebDriverWait(self.driver,5).until(ec.presence_of_element_located((By.ID,element_identifier)))
            elif element.lower()=='class':
                #intenter con class
                a=WebDriverWait(self.driver,5).until(ec.presence_of_element_located((By.CLASS_NAME,element_identifier)))
            elif element.lower()=='xpath':
                #intenter con class
                a=WebDriverWait(self.driver,5).until(ec.presence_of_element_located((By.XPATH,element_identifier)))
            # print('elemento encontrado correctamente: ',element_identifier)
            time.sleep(1)

        except:#implicit waits
            print("error al identificar:{}: {}\nespera 30 segundos".format(element,element_identifier))
            time.sleep(5)
            a=''
        return a

    def __login(self,social,user,password):
        '''
        social= social network [instagram,facebook,twitter]
        '''
        #login function, setting user and password
        print('Login into:',social.lower())
        time.sleep(5)
        self.driver.get(self.platform[social.lower()]['login_url'])
        self.user=user
        #writing username
        try:
            user_box=self.__wait(self.platform[social.lower()]['userbox'])
            user_box.send_keys(user)
            user_box.send_keys(Keys.ENTER)
        except:
            pass

        #writing password
        try:
            pass_box=self.__wait(self.platform[social.lower()]['passbox'])
            pass_box.send_keys(password)
        except:
            print('no password box found')
        pass_box.send_keys(Keys.ENTER)
        self.__wait(self.platform[social]['landing_page'])

    def __profile_info(self,social,user):
        '''
        social: instagram/facebook/twitter
        '''
        try:
            self.driver.get(self.platform[social]['main_url']+user)
        except:
            pass
        self.__wait(self.platform[social]['profile_insight'])
        content=self.driver.page_source
        soup=BeautifulSoup(content,'html.parser')
        z=[x.text.strip() for x in soup.find_all(attrs=self.platform[social]['profile_insight'])]
        print(z)

    def __get_posts_link(self,social,user):
        '''
        reading posts links
        social: instagram/facebook/twitter
        '''
        # self.posts_links=[]
        print('getting post links')
        self.driver.get(self.platform[social]['main_url']+user)
                
        #reload windows until obtaining desired page/results
        z=self.__wait(self.platform[social]['posts-pages'])
        while z=='':
            self.driver.refresh()
            z=self.__wait(self.platform[social]['posts-pages'])
        content=self.driver.page_source
        soup=BeautifulSoup(content,'html.parser')
        self.posts=[]
        for x in soup.find_all(attrs=self.platform[social]['posts']):
            try:
                # print(x.a.get('href'))
                self.posts.append(x.a.get('href'))
            except:
                pass

    def __get_post_insights(self,social):
        '''
        get post insights
        '''
        print('getting post insight')
        for a in self.posts:
            self.driver.get(self.platform[social]['main_url']+a[1:])
            print(self.platform[social]['main_url']+a)
            intentos=5
            while True:
                insight=self.__wait(self.platform[social]['insight'])
                if insight=='' and intentos>0:
                    self.driver.refresh()
                    intentos-=1
                else:
                    break
            try:
                insight.send_keys(Keys.ENTER)
            except:
                pass
            time.sleep(5)
            if intentos>0:
                content=self.driver.page_source
                soup=BeautifulSoup(content,'html.parser')
                items=0
                self.info['post'].append(self.platform[social]['main_url']+a[1:])
                for b in soup.find_all(attrs=self.platform[social]['post_insight']):
                    if b.text.isnumeric() and items<len(self.platform[social]['categories']):
                        print('{}:  {}'.format(self.platform[social]['categories'][items],b.text.strip()))
                        self.info[self.platform[social]['categories'][items]].append(b.text.strip())
                        items+=1
                    else:
                        # self.info[self.platform[social]['categories'][items]].append('0')
                        print(b)
            else:
                print('este post no despliega la informacion de insight')
                continue


    def instagram(self,user,password):
        site='instagram'
        self.__login(site,user,password)
        # self.__profile_info(site,user)
        self.__get_posts_link(site,user)
        self.__get_post_insights(site)

    def facebook(self, user, password):
        site='facebook'
        self.__login(site,user,password)
        # self.__profile_info(site,'profile')

    def twitter(self,user,password):
        site='twitter'
        self.__login(site,user,password)
        # self.__profile_info(site,user)
        self.__get_posts_link(site,user)
        self.__get_post_insights(site)
    
    def close(self):
        for y in self.info.keys():
            print('{} {}'.format(y,len(self.info[y])))
        try:
            z=pd.DataFrame(self.info)
            print(z)
            z.to_csv('social_media_scrapping.csv')
        except:
            print('no se pudo transformar a pandas diferencias de longitudes')
        self.driver.quit()

if __name__=="__main__":
    insta=social_media()
    print('*'*50,'testing','*'*50)
    insta.instagram('cidetysaip','Cidetys20UTP$')
    # insta.facebook('cidetysaip@gmail.com','Cidetys*2020')
    insta.twitter('Cidetysaip','*Cidetys*20*20')
    print('closing session')
    time.sleep(5)
    insta.close()

#sugerencias
##cuantos mensajes directos recibido en la ultima hora
# cantidad de like del ultimo post
# determinar quien esta activo de manera horaria, aumento la prob de que vea el post
# hacer demo de control de UI
# averiguar que ofrecer instagram business


#facebook
#cuenta personal= amigos
#cuenta empresarial=me gusta
# me gusta!= me siguen ???