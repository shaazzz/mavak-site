
<div align="right" style="direction:rtl;text-align:right;">

سورس کد سایت 

https://mavak.shaazzz.ir

# توضیحات سایت 

## ماواک چیست؟
در سال های اخیر، المپیاد در انحصار مدارس بزرگ کلان شهر ها قرار گرفته است. این موضوع در المپیاد کامپیوتر، به دلیل شرایط ویژه آن مانند کمتر شناخته شده بودن آن یا دور بودن آن از منابع کتاب درسی، شدید تر است. مدرسه استعداد یابی و آموزش المپیاد کامپیوتر (ماواک)، دقیقا برای رفع این معضل به وجود آمده است. ماواک با بهره گیری از تجارب مدارس بزرگ در تلاش است که این شرایط را برای دانش آموزان دیگر شهر ها نیز فراهم کند


### ساختار

دانش آموزانی که در آزمون ورودی ماواک پذیرفته می شوند، در یک برنامه منظم مطالب و تمرین ها در اختیارشان گذاشته می شود و در بازه های زمانی کوتاه از آن ها آزمون گرفته می شود. گزارش تحلیل شده از تمارین و آزمون ها در اختیار والدین و مدارس قرار داده می شود و به وسیله آن در مورد ادامه مسیر تصمیم گیری می شود. هم چنین پشتیبان وضعیت دانش آموز را پیگیری می کند و به سوال های او پاسخ می دهد. تا حد امکان سعی شده است که ماواک شرایط مدارس بزرگ را شبیه سازی کند


### هزینه

ماواک توسط داوطلبان اداره می شود و کاملا ناسودبر و عام المنفعه است. بنابراین در هیچ جایی از این برنامه هیچ هزینه ای از شما دریافت نمی شود. این در حالی ست که مدارس برای دانش آموزان خودشان، میلیون ها تومان (جدای از شهریه) برای کلاس های المپیاد دریافت می کنند و موسسات خصوصی، صد ها هزار تومان برای کلاس هایی در بازه زمانی کوتاه یا برای حتی یک آزمون دریافت می کنند. اما ماواک یک برنامه یک ساله کاملا رایگان و کامل (از لحاظ تدریس، تمرین و آزمون) است.


## نصب و راه اندازی

#### نصب و اجرا برای تست

<div align="left" style="direction:ltr;text-align:left;">
 
```
git clone https://github.com/shaazzz/mavak-site.git
cd mavak-site
pip3 install -r requirements.txt
export DJANGO_SETTINGS_MODULE=mavaksite.settings.development
python3 manage.py migrate
python3 manage.py runserver
```
 
</div>
در این حالت debug  فعال خواهد بود

#### نصب و اجرا روی سرور

<div align="left" style="direction:ltr;text-align:left;">
 
```
git clone https://github.com/shaazzz/mavak-site.git
cd mavak-site
pip3 install -r requirements.txt
export DJANGO_SETTINGS_MODULE=mavaksite.settings.production
python3 manage.py migrate
python3 manage.py runserver
```

</div>
در این حالت debug  غیرفعال خواهد بود


## توضیحات پنل ادمین
 برای استفاده از پنل ادمین ابتدا یک superuser بسازید:
<div align="left" style="direction:ltr;text-align:left;">
 
```
python3 manage.py createsuperuser
Username: admin
Email address: admin@example.com
Password: **********
Password (again): *********
Superuser created successfully.

```
</div>

سپس وارد لینک 

https://mavak.shaazzz.ir/admin

شوید، در حال حاضر پنل ادمین به شکل زیر است:

![file](https://github.com/shaazzz/mavak-site/raw/master/documentation/files/admin-panel.png)

(این قسمت در آینده کامل خواهد شد)


## توضیحات استفاده برای کاربران

(این قسمت در آینده کامل خواهد شد)

![file](https://github.com/shaazzz/mavak-site/raw/master/documentation/files/users-login.png)

![file](https://github.com/shaazzz/mavak-site/raw/master/documentation/files/users-create-account-student.png)

![file](https://github.com/shaazzz/mavak-site/raw/master/documentation/files/profile.png)


