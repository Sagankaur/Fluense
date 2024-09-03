from .database import db

class User(db.Model): #all user
    id = db.Column(db.Integer(), primary_key = True, autoincrement=True)
    username = db.Column(db.String(), nullable = False, unique = True)
    password = db.Column(db.String(), nullable = False)
    type = db.Column(db.String(), default = "admin", nullable= False)
    flag = db.Column (db.Boolean(), default= False )
    
    influencer = db.relationship("Influencer", backref="user", uselist=False, cascade="all, delete-orphan")  # one-to-one relation with Influencer
    sponsor = db.relationship("Sponsor", backref="user", uselist=False, cascade="all, delete-orphan")  # one-to-one relation with Sponsor
    
class Add_campaign(db.Model):
    id = db.Column(db.Integer(), primary_key = True,autoincrement=True)
    
    sponsor_id = db.Column(db.Integer(), db.ForeignKey("sponsor.id", ondelete='CASCADE')) #1 Sponsor => MANY Campaign 
    
    title = db.Column(db.String(), nullable = False, unique=True)
    description = db.Column(db.String())
    image = db.Column(db.String(), nullable = True)
    niche = db.Column(db.String(), nullable = False)
    s_date = db.Column(db.String(), nullable = False)
    e_date = db.Column(db.String(), nullable = False, default = "To be updated")
    budget = db.Column(db.Integer(), default = 1000)
    visibility = db.Column(db.String(), default = "private")
    status = db.Column(db.String(), default = "in-process") #in-process/ completed
    flag = db.Column (db.Boolean(), default= False )
    goals = db.Column(db.String())
    
    ad_reqs = db.relationship("Ad_request", backref="campaign", cascade="all, delete-orphan") #ONE camp=> many reqs

class Ad_request(db.Model):
    id = db.Column(db.Integer(), primary_key = True, autoincrement=True)
    
    sponsor_id = db.Column(db.Integer(), db.ForeignKey("sponsor.id", ondelete='CASCADE'),nullable= False) #when row in parent table is deleted, it will also delete
    influencer_id = db.Column(db.Integer(), db.ForeignKey("influencer.id" , ondelete='CASCADE'),nullable= False) #1 sponsor=> MANY ad req
    campaign_id = db.Column(db.Integer(), db.ForeignKey("add_campaign.id", ondelete='CASCADE'),nullable= False) #1 campaign=> MANY ad requests
    
    messages = db.Column(db.String(), nullable = True)
    requirements = db.Column(db.String())
    pay = db.Column(db.Integer(), default = 0)
    status = db.Column(db.String(), default = "pending") #pending/ rejected/ accpeted
    #user_id = db.Column(db.Integer(), db.ForeignKey("user.id")) #1 sponsor=> MANY ad req
    
class Influencer(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer(), db.ForeignKey("user.id"),primary_key=True)
    
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    phone = db.Column(db.Integer, nullable=True)
    flw = db.Column(db.Integer, default=0)
    category = db.Column(db.String, nullable=False)
    niche = db.Column(db.String, nullable=True)
    platform_presence = db.Column(db.String, nullable=True)
    profile_pic= db.Column(db.String(120), nullable=True)
    
    camps = db.relationship("Ad_request", backref = "influencer", cascade="all, delete-orphan")

class Sponsor(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer(), db.ForeignKey("user.id"),primary_key=True)
    
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    industry = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    
    camps = db.relationship("Add_campaign", backref = "sponsor", cascade="all, delete-orphan")
    ad_reqs = db.relationship("Ad_request", backref = "sponsor", cascade="all, delete-orphan")

#user_1.add_campaign = campaigns of a user_1
#who has created add_campaign_1 = add_campign_1.user = user of this camp_1 = inside(backref) of outside(class object)