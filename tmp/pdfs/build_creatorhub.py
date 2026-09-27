import re,json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
pdfmetrics.registerFont(TTFont('Arial','/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialB','/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
OUT='/Users/kakhkhorov/Desktop/Nestar/output/pdf/creatorhub-er-connections-uz-en.pdf'
c=canvas.Canvas(OUT,pagesize=(660,880));c.setTitle('CreatorHub ER connections | Uzbek and English');c.setAuthor('CreatorHub review')
navy='#152C44';teal='#087F8C';muted='#526579';page=0
style=ParagraphStyle('body',fontName='Arial',fontSize=11,leading=16,textColor=HexColor(navy))
def para(text,x,y,w=564,size=11,color=navy):
 st=ParagraphStyle('p',parent=style,fontSize=size,leading=size*1.42,textColor=HexColor(color));p=Paragraph(text,st);_,h=p.wrap(w,800);p.drawOn(c,x,y-h);return y-h

def start(title,uz,desc=''):
 global page
 page+=1;c.setFillColor(HexColor('#F5F8FB'));c.rect(0,0,660,880,fill=1,stroke=0)
 c.setFillColor(HexColor(teal));c.rect(0,860,660,20,fill=1,stroke=0)
 para('CREATORHUB / ER CONNECTIONS',48,828,size=10,color=teal)
 para(title,48,800,size=24);para(uz,48,762,size=15,color=muted)
 if desc:para(desc,48,729,size=11)
 c.setStrokeColor(HexColor('#D7E1E9'));c.line(48,48,612,48)
 para('Updated model review / Yangilangan model tekshiruvi',48,35,size=9,color=muted)
 para(str(page),590,35,w=30,size=9,color=muted)
def end():c.showPage()
def arrow(x1,y,x2,color=teal,dash=False):
 c.setStrokeColor(HexColor(color));c.setLineWidth(1.5)
 if dash:c.setDash(3,3)
 c.line(x1,y,x2,y);c.setDash();c.line(x2-7,y+4,x2,y);c.line(x2-7,y-4,x2,y)
def box(x,y,w,head,field):
 c.setFillColor(HexColor('#E7F2F4'));c.setStrokeColor(HexColor('#ADD2D7'));c.roundRect(x,y,w,48,7,fill=1,stroke=1)
 para(head,x+10,y+38,w=w-20,size=11);para(field,x+10,y+20,w=w-20,size=10,color=teal)
def connection(child,field,parent,y):
 box(48,y,246,child,field);box(378,y,234,parent,'_id');arrow(306,y+24,367)
 para('references',302,y+44,w=78,size=8,color=muted)

rows={}
s=open('/Users/kakhkhorov/Desktop/docs/CreatorHub-ER-modeling-guide.md').read()
for line in s.splitlines():
 if re.match(r'\| R\d\d \|',line):
  _,rid,parent,field,pc,cp,label,_=[x.strip() for x in line.split('|')];ch,fn=field.split('.');rows[int(rid[1:])]=(rid,parent,ch,fn,pc,cp)
texts={
1:('A profile belongs to one user. A user may have no profile or one profile.','Profil bitta foydalanuvchiga tegishli. Foydalanuvchida profil bo\'lmasligi yoki bitta profil bo\'lishi mumkin.'),
2:('A profile stores up to five distinct category IDs. Many profiles may use the same category. At least one is needed to publish.','Profil ko\'pi bilan beshta turli kategoriya ID sini saqlaydi. Bitta kategoriyani ko\'p profil tanlashi mumkin. Profilni e\'lon qilish uchun kamida bittasi kerak.'),
3:('Each project belongs to one creator profile. One creator can publish many projects.','Har bir loyiha bitta ijodkor profiliga tegishli. Bitta ijodkor ko\'p loyiha e\'lon qilishi mumkin.'),
4:('A project can have no category while it is a draft. Publishing requires one active category.','Loyiha qoralama paytida kategoriyasiz bo\'lishi mumkin. E\'lon qilish uchun bitta faol kategoriya kerak.'),
5:('Each service belongs to one creator profile. One creator can offer many services.','Har bir xizmat bitta ijodkor profiliga tegishli. Bitta ijodkor ko\'p xizmat taklif qilishi mumkin.'),
6:('A draft service can have no category. Activating it requires one active category.','Qoralama xizmat kategoriyasiz bo\'lishi mumkin. Uni faollashtirish uchun bitta faol kategoriya kerak.'),
7:('The like records which user liked the project. One user can like many projects.','Laykni qaysi foydalanuvchi bosganini saqlaydi. Bitta foydalanuvchi ko\'p loyihaga layk bosishi mumkin.'),
8:('The like records its target project. One project can receive many likes.','Layk qaysi loyihaga tegishli ekanini saqlaydi. Bitta loyiha ko\'p layk olishi mumkin.'),
9:('The save records the user who bookmarked the project.','Saqlash yozuvi loyihani xatcho\'pga qo\'shgan foydalanuvchini ko\'rsatadi.'),
10:('The save records the bookmarked project. A project can be saved by many users.','Saqlash yozuvi xatcho\'pga qo\'shilgan loyihani ko\'rsatadi. Bitta loyihani ko\'p foydalanuvchi saqlashi mumkin.'),
11:('Each comment has one author. A user can write many comments.','Har bir izohning bitta muallifi bor. Foydalanuvchi ko\'p izoh yozishi mumkin.'),
12:('Each comment belongs to one project. Comments have no reply-to-comment reference.','Har bir izoh bitta loyihaga tegishli. Izohlar orasida boshqa izohga javob havolasi yo\'q.'),
13:('The client is the user sending the inquiry. A creator account can also act as a client.','Mijoz so\'rov yuborayotgan foydalanuvchidir. Ijodkor akkaunti ham mijoz sifatida so\'rov yuborishi mumkin.'),
14:('The inquiry targets one creator profile. Its owner is found through creatorProfiles.userId.','So\'rov bitta ijodkor profiliga yuboriladi. Profil egasi creatorProfiles.userId orqali topiladi.'),
15:('Selecting a service is optional. If present, the service must belong to the inquiry\'s creator.','Xizmat tanlash ixtiyoriy. Xizmat tanlansa, u so\'rov yuborilgan ijodkorga tegishli bo\'lishi kerak.'),
16:('This optional ID records the user who closed or cancelled the inquiry.','Bu ixtiyoriy ID so\'rovni yopgan yoki bekor qilgan foydalanuvchini ko\'rsatadi.'),
17:('Each message belongs to one inquiry. An inquiry can contain many messages.','Har bir xabar bitta so\'rovga tegishli. Bitta so\'rovda ko\'p xabar bo\'lishi mumkin.'),
18:('Each message has one sender. The sender must be an inquiry participant.','Har bir xabarning bitta yuboruvchisi bor. U so\'rov ishtirokchisi bo\'lishi kerak.'),
19:('Each history event belongs to one inquiry. One inquiry can have many events.','Har bir tarixiy voqea bitta so\'rovga tegishli. Bitta so\'rovda ko\'p voqea bo\'lishi mumkin.'),
20:('performedById records who performed the action. It references users, not creatorProfiles.','performedById amalni kim bajarganini ko\'rsatadi. U creatorProfiles ga emas, users ga bog\'lanadi.'),
21:('Only a MESSAGE_SENT event has messageId. Each committed message has exactly one message event.','Faqat MESSAGE_SENT voqeasida messageId bor. Har bir saqlangan xabar uchun aynan bitta xabar voqeasi bo\'ladi.'),
22:('recipientId is the notification inbox owner. It is not the user who performed the action.','recipientId bildirishnoma oluvchidir. U amalni bajargan foydalanuvchini anglatmaydi.'),
23:('An inquiry notification points to one inquiry event. Each committed inquiry event produces one notification for the other participant.','So\'rov bildirishnomasi bitta so\'rov voqeasiga bog\'lanadi. Har bir saqlangan so\'rov voqeasi boshqa ishtirokchi uchun bitta bildirishnoma yaratadi.'),
24:('Each session belongs to one account. An account can have many sessions.','Har bir sessiya bitta akkauntga tegishli. Akkauntda ko\'p sessiya bo\'lishi mumkin.'),
25:('A verification or reset token targets one EMAIL identity. It does not point directly to users.','Tasdiqlash yoki parolni tiklash tokeni bitta EMAIL kirish usuliga tegishli. U users ga bevosita bog\'lanmaydi.'),
26:('Each identity belongs to one account. An account retains one to five identities, at most one per provider.','Har bir kirish usuli bitta akkauntga tegishli. Akkauntda bittadan beshtagacha kirish yozuvi bo\'ladi, har bir provayder uchun ko\'pi bilan bittadan.'),
27:('The session records the login method used. Its userId must match that identity\'s userId.','Sessiya qaysi kirish usuli ishlatilganini saqlaydi. Uning userId qiymati shu kirish usulining userId qiymatiga teng bo\'lishi kerak.'),
28:('followerId is the user following the creator. A user can follow many creators.','followerId ijodkorga obuna bo\'lgan foydalanuvchidir. Foydalanuvchi ko\'p ijodkorga obuna bo\'lishi mumkin.'),
29:('creatorId is the followed profile. It is a profile ID, not a user ID.','creatorId obuna bo\'lingan profildir. Bu foydalanuvchi ID si emas, profil ID sidir.'),
30:('The performer is the publisher, liking user, comment author, or follower, depending on the event.','Voqeaga qarab amalni bajaruvchi loyiha egasi, layk bosgan foydalanuvchi, izoh muallifi yoki obunachidir.'),
31:('Every activity event identifies the creator profile it concerns.','Har bir faollik voqeasi qaysi ijodkor profiliga tegishli ekanini ko\'rsatadi.'),
32:('Project publication, like, and comment events require projectId. A creator-follow event has no projectId.','Loyiha e\'loni, layk va izoh voqealarida projectId kerak. Ijodkorga obuna voqeasida projectId bo\'lmaydi.'),
33:('Only PROJECT_COMMENTED has commentId. Each new comment has exactly one creation event.','Faqat PROJECT_COMMENTED voqeasida commentId bor. Har bir yangi izoh uchun aynan bitta yaratilish voqeasi bo\'ladi.'),
34:('An activity event can produce zero or many notifications. Many follower alerts may point to the same publication event.','Faollik voqeasi nol yoki ko\'p bildirishnoma yaratishi mumkin. Ko\'p obunachining bildirishnomasi bitta loyiha e\'loni voqeasiga bog\'lanishi mumkin.')}
def card(n,y,h):
 rid,parent,ch,fn,pc,cp=rows[n]
 para(rid,48,y,size=10,color=teal);connection(ch,fn,parent,y-68)
 y2=y-80;en,uz=texts[n];y2=para('EN  '+en,48,y2,size=10.5);y2=para('UZ  '+uz,48,y2-5,size=10.5)
 para('Parent per record / Yozuvga ota yozuv: '+pc+'     |     Records per parent / Otaga yozuvlar: '+cp,48,y2-7,size=9,color=muted)
 assert y2-25>y-h, (n,y2,y-h)

start('How to read a connection','Bog\'lanishni qanday o\'qish kerak')
connection('creatorProfiles','userId = U1','users',630)
para('EN  The arrow points from the stored reference to the record it identifies. Here, creatorProfiles.userId stores the value of users._id.',48,605)
para('UZ  Strelka saqlangan havoladan u ko\'rsatadigan yozuvga qaraydi. Bu yerda creatorProfiles.userId ichida users._id qiymati saqlanadi.',48,548)
para('1 = exactly one / aynan bitta<br/>0..1 = absent or one / yo\'q yoki bitta<br/>0..* = zero or many / nol yoki ko\'p<br/>1..5 = one to five / bittadan beshtagacha',48,464,size=13)
para('EN  Read both counts separately. A profile needs one user, but a user can have no profile. The arrow shows lookup direction, not creation order.',48,345)
para('UZ  Ikkala sonni alohida o\'qing. Profilga bitta foydalanuvchi kerak, lekin foydalanuvchida profil bo\'lmasligi mumkin. Strelka yaratish tartibini emas, qaysi yozuvni topishni ko\'rsatadi.',48,288)
para('Reviewed: CreatorHub-connected.dmm and the revised ER guide. All 34 reference endpoints and counts match. This document covers connections only.',48,177,size=10,color=muted)
para('Tekshirildi: CreatorHub-connected.dmm va yangilangan ER qo\'llanmasi. 34 havolaning maydonlari va sonlari mos. Bu hujjat faqat bog\'lanishlarni tushuntiradi.',48,127,size=10,color=muted);end()
groups=[
('Account, profile and work','Akkaunt, profil va ishlar',[1,2,3]),
('Categories and services','Kategoriyalar va xizmatlar',[4,5,6]),
('Likes and saved projects','Layklar va saqlangan loyihalar',[7,8,9,10]),
('Comments and creator follows','Izohlar va ijodkorga obunalar',[11,12,28,29]),
('Who sends and receives an inquiry','So\'rovni kim yuboradi va kim oladi',[13,14,15,16]),
('Messages and inquiry history','Xabarlar va so\'rov tarixi',[17,18,19]),
('Who acted, and which message','Amalni kim bajardi va qaysi xabar',[20,21]),
('Accounts and login identities','Akkauntlar va kirish usullari',[24,26,27]),
('Email tokens and notification sources','Email tokenlari va bildirishnoma manbalari',[25,22,23]),
('Public activity references','Ommaviy faollik havolalari',[30,31,32]),
('Comments and activity notifications','Izohlar va faollik bildirishnomalari',[33,34])]
for title,uz,ids in groups:
 start(title,uz)
 h=153 if len(ids)==4 else 200
 for i,n in enumerate(ids):card(n,710-i*h,h)
 if ids==[20,21]:
  para('EN  Example: inquiry I1 contains message M1. Its MESSAGE_SENT event stores inquiryId = I1, messageId = M1 and performedById = the sender\'s user ID.',48,270)
  para('UZ  Misol: I1 so\'rovda M1 xabar bor. MESSAGE_SENT voqeasi inquiryId = I1, messageId = M1 va performedById = yuboruvchining user ID sini saqlaydi.',48,207)
 if ids==[33,34]:
  para('EN  A notification must have inquiryEventId OR activityEventId. Exactly one is present. Both missing or both present is invalid.',48,270)
  para('UZ  Bildirishnomada inquiryEventId YOKI activityEventId bo\'lishi shart. Aynan bittasi bo\'ladi. Ikkalasi ham yo\'q yoki ikkalasi ham bor bo\'lsa, yozuv noto\'g\'ri.',48,213)
 end()
start('Embedded data is containment','Ichki ma\'lumot yozuv ichida saqlanadi')
for y,owner,field,obj,en,uz in [
(650,'creatorProfiles','socialLinks[]','SocialLink','Website links live inside the profile. They are not references to a separate collection.','Sayt havolalari profil ichida saqlanadi. Ular alohida kolleksiyaga havola emas.'),
(450,'portfolioProjects','media[]','PortfolioMedia','Media entries live inside the project. The URL is a file link, not a collection ID.','Media yozuvlari loyiha ichida saqlanadi. URL faylga havola, kolleksiya ID si emas.'),
(250,'inquiries','serviceSnapshot','InquiryServiceSnapshot','The snapshot copies service details at submission. It stays unchanged when the service changes. Only serviceId references services.','So\'rov yuborilganda xizmat tafsilotlari nusxalanadi. Xizmat o\'zgarsa ham nusxa o\'zgarmaydi. Faqat serviceId services ga bog\'lanadi.')]:
 box(48,y,246,owner,field);box(378,y,234,obj,'embedded / ichki');arrow(306,y+24,367,dash=True)
 para('EN  '+en,48,y-15);para('UZ  '+uz,48,y-62)
end()
start('Connection rules to keep together','Birgalikda tekshiriladigan qoidalar')
items=[
('creatorId points to creatorProfiles._id. userId, clientId, senderId, followerId, recipientId and performedById point to users._id.','creatorId creatorProfiles._id ga bog\'lanadi. userId, clientId, senderId, followerId, recipientId va performedById users._id ga bog\'lanadi.'),
('A like or save links a user and a project. The user + project pair is unique. A follow links a user and a creator profile, also as a unique pair.','Layk yoki saqlash foydalanuvchi bilan loyihani bog\'laydi. user + project juftligi takrorlanmaydi. Obuna foydalanuvchi bilan ijodkor profilini bog\'laydi, bu juftlik ham takrorlanmaydi.'),
('IDs must agree: the selected service belongs to the inquiry creator; the event message belongs to that inquiry; the activity comment belongs to that project and creator.','ID lar mos bo\'lishi kerak: tanlangan xizmat so\'rovdagi ijodkorniki; voqea xabari o\'sha so\'rovniki; faollik izohi o\'sha loyiha va ijodkorniki.'),
('MongoDB references do not automatically enforce ownership, required event creation or cascading deletion. The application checks these rules. Soft deletion keeps historical references.','MongoDB havolalari egalikni, kerakli voqea yaratilishini yoki bog\'liq yozuvlar o\'chirilishini avtomatik boshqarmaydi. Ilova bu qoidalarni tekshiradi. Yumshoq o\'chirish tarixiy havolalarni saqlaydi.')]
y=713
for en,uz in items:
 y=para('EN  '+en,48,y);y=para('UZ  '+uz,48,y-6);y-=23
para('Review result / Tekshiruv natijasi',48,y,size=15,color=teal);y-=28
para('17 collections + 3 embedded object definitions; 34 references + 3 containment lines. All 34 parent fields are _id. Endpoints and counts match the guide. This is a structural review, not a live database test.',48,y,size=10)
y-=63
para('Sources / Manbalar<br/>Desktop/Creator hub/CreatorHub-connected.dmm<br/>Desktop/docs/CreatorHub-ER-modeling-guide.md, sections 5 and 7<br/>Reviewed on 27 September 2026.',48,y,size=9,color=muted)
end();c.save();print(OUT)
