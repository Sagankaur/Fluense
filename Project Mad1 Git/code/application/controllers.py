from flask import Flask, request, render_template, redirect, flash
import os
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import numpy as np
from flask import current_app as app
from sqlalchemy import and_
from .models import *
from flask import session
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads') 
#app=None

@app.route("/",methods=["GET","POST"])
@app.route("/user_login",methods=["GET","POST"])
def user_login():
    if request.method == "POST":
        u_name = request.form.get('u_name')
        pwd = request.form.get('pwd')
        this_user= User.query.filter_by(username = u_name).first()
        print (f'Login for u_name={u_name}') 
        if this_user:
            if this_user.password == pwd:
                if not(this_user.flag):
                    session['username'] = this_user.username
                    if this_user.type.lower() == 'influencer':
                        return redirect(f'/influencer_profile_dashboard/{this_user.id}') 
                    elif  this_user.type.lower() == 'sponsor':
                        return redirect(f'sponsor_profile_dashboard/{this_user.id}')
                    elif  this_user.type.lower() == 'admin':
                        return redirect('/admin_info_dashboard')
                else:
                    return 'User is Flagged. You can NOT login.'
            else: 
                return 'wrong password'
        else: 
            return 'wrong username' 
    return render_template('user_login.html')

#registers
@app.route("/influencer_register", methods=["GET", "POST"])
def influencer_register():
    if request.method == "POST":
        u_name = request.form.get('u_name')
        pwd = request.form.get('pwd')
        name = request.form.get('name')
        email = request.form.get('email')
        category = request.form.get('category')
        niche = request.form.get('niche')
        phone = request.form.get('phone')
        flw = request.form.get('flw')
        platform_presence = request.form.getlist('platform_presence')
        file = request.files.get('img')
        ALLOWED_EXTENSIONS = {'png'}
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        image_filename = None
        if file and allowed_file(file.filename):        
            original_filename = file.filename
            image_filename = (f"profile_{u_name}.{original_filename.rsplit('.', 1)[1].lower()}")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(file_path)
            
        this_user = User.query.filter_by(username=u_name).first()
        if this_user:
            return 'Username already exists'
        else:
            new_user = User(username=u_name, 
                            password=pwd, 
                            type='influencer')
            db.session.add(new_user)
            db.session.commit()  # Commit to get the new user ID
            session['username'] = new_user.username
            new_influencer = Influencer(
                id=new_user.id,
                name=name,
                email=email,
                phone=phone,
                category=category,
                niche=niche,
                platform_presence=", ".join(platform_presence),  # Join list into a string
                profile_pic=image_filename,
                flw=flw)
            
            db.session.add(new_influencer)
            db.session.commit()
            print(f'Redirecting to /influencer_profile_dashboard/{new_user.id}')
            return redirect(f'/influencer_profile_dashboard/{new_user.id}') 
    return render_template('influencer_register.html')

@app.route("/sponsor_register",methods=["GET","POST"])
def sponsor_register():
    if request.method == "POST":
        u_name= request.form.get('u_name')
        pwd= request.form.get('pwd')
        name= request.form.get('name')
        email= request.form.get('email')
        industry= request.form.get('industry')
        budget= request.form.get( 'budget')
        phone= request.form.get('phone')
        this_user= User.query.filter_by(username = u_name).first()
        if this_user:
            return 'user name already exists'
        else:
            new_user = User(username=u_name, password=pwd, type='sponsor')
            db.session.add(new_user)
            db.session.commit()  # Commit to get the new user ID
            session['username'] = new_user.username
            new_sponsor = Sponsor(
                id=new_user.id,
                name=name,
                email=email,
                phone=phone,
                industry=industry,
                budget=budget
            )
            
            db.session.add(new_sponsor)
            db.session.commit()
            return redirect(f'/sponsor_profile_dashboard/{new_user.id}')
    return render_template('sponsor_register.html')

#redirects to profile

@app.route('/influencer_profile_dashboard/<int:user_id>', methods=['GET', 'POST'])
def influencer_profile_dashboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return "User not found"
    influencer = Influencer.query.get(user_id)
    if not influencer:
        return "Influencer details not found"
    accept_req = Ad_request.query.filter_by(influencer_id=user_id, status='Accepted').all()
    new_requests = Ad_request.query.filter_by(influencer_id=user_id, status='Pending').all()
    for req in accept_req:
        if req:
            earnings = sum((req.pay.strip()))
        else: 
            earnings= 0
    reach=len(accept_req)
    
    return render_template('influencer_profile_dashboard.html',  u_name=user.username,
                           influencer=influencer,
                           new_requests=new_requests,accept_req=accept_req,
                           earnings=earnings, user=user, reach=reach)

@app.route('/sponsor_profile_dashboard/<int:user_id>', methods=['GET', 'POST'])
def sponsor_profile_dashboard(user_id):
    user = User.query.get(user_id)
    if not user:
        return "User not found"
  
    sponsor = Sponsor.query.get(user_id)
    if not sponsor:
        return "Sponsor details not found"

    ad_requests = Ad_request.query.filter_by(sponsor_id=user_id).all()
    accepted_req = [request for request in ad_requests if request.status == 'Accepted']
    rejected_req = [request for request in ad_requests if request.status == 'Rejected']
    pending_req = [request for request in ad_requests if request.status == 'Pending']

    return render_template('sponsor_profile_dashboard.html',  u_name=user.username,
    ad_requests=ad_requests , 
    sponsor=sponsor, user=user,
    accepted_req=accepted_req,rejected_req=rejected_req,pending_req=pending_req)

#update profile influencer
@app.route("/update_profile_influencer/<int:influencer_id>", methods=["GET", "POST"])
def update_profile_influencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    
    if request.method == "POST":
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        category = request.form.get('category')
        niche = request.form.get('niche')
        flw = request.form.get('flw')
        platform_presence = request.form.getlist('platform_presence')
        
        # Update influencer's details
        influencer.name = name
        influencer.email = email
        influencer.phone = phone
        influencer.category = category
        influencer.niche = niche
        influencer.flw = flw
        influencer.platform_presence = ", ".join(platform_presence)
        
        db.session.commit()
        return redirect(f'/influencer_profile_dashboard/{influencer_id}')
    
    return render_template('update_profile_influencer.html', influencer=influencer)

@app.route("/update_profile_pic/<influencer_id>", methods=["POST"])
def update_profile_pic(influencer_id):
    user_id =influencer_id
    
    file = request.files.get('img')
    ALLOWED_EXTENSIONS = {'png'}
    
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if file and allowed_file(file.filename):
        original_filename = file.filename
        image_filename = f"profile_{user_id}.{original_filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(file_path)
        
        influencer = Influencer.query.filter_by(id=user_id).first()
        if influencer:
            influencer.profile_pic = image_filename
            db.session.commit()
        
        return redirect(f'/influencer_profile_dashboard/{user_id}')
    else:
        return "Invalid file type", 400

#admin dashboard

@app.route("/admin_find_dashboard",methods=["GET","POST"])
def admin_find_dashboard():
    search_query = request.form.get('search', '')  # Retrieve search input, default= ''
    influencers = []
    sponsors = []
    campaigns = []
    
    if search_query:
        influencers = Influencer.query.filter(Influencer.name.ilike(f'%{search_query}%')).all()
        sponsors = Sponsor.query.filter(Sponsor.name.ilike(f'%{search_query}%')).all()
        campaigns = Add_campaign.query.filter(
            Add_campaign.title.ilike(f'%{search_query}%')
        ).all()
    
    return render_template(
        "admin_find_dashboard.html",
        influencers=influencers,
        sponsors=sponsors,
        campaigns=campaigns
    )

@app.route("/admin_info_dashboard",methods=["GET","POST"])
def admin_info_dashboard():
    admin= User.query.filter_by(type='admin').first()
    ongoing_campaigns = Add_campaign.query.filter_by(status='in-process',flag=False).all()
    flagged_campaigns = Add_campaign.query.filter_by(flag=True).all()
    flagged_users = User.query.filter_by(flag=True).all()
    return render_template("admin_info_dashboard.html", u_name=admin.username,
                           ongoing_campaigns=ongoing_campaigns,
                           flagged_campaigns=flagged_campaigns,
                           flagged_users=flagged_users)

@app.route("/admin_stats_dashboard",methods=["GET","POST"])
def admin_stats_dashboard():
    influencers = Influencer.query.all()
    sponsors = Sponsor.query.all()
    campaigns = Add_campaign.query.all()
    ad_requests = Ad_request.query.all()
    
    influencer_niches = [influencer.niche for influencer in influencers]
    sponsor_types = [sponsor.industry for sponsor in sponsors]
    campaign_statuses = [campaign.status for campaign in campaigns]
    ad_request_statuses = [ad_request.status for ad_request in ad_requests]
    if influencer_niches:
        plt.clf()
        plt.hist(influencer_niches, bins=range(len(set(influencer_niches)) + 1), edgecolor='black')
        plt.title('Influencer Niches Distribution')
        plt.xlabel('Niche')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.savefig('static/influencer_niches.png')
    elif not(influencer_niches):
        plt.clf()
        plt.text(0.5, 0.5,'No Influencer')
        plt.title('No Data')
        plt.xlabel('Niche') 
        plt.ylabel('Count')
        plt.xticks([])
        plt.yticks(np.arange(0, 1, step=1))
        plt.tight_layout()
        plt.savefig('static/influencer_niches.png')

    if sponsor_types:
        plt.clf()
        plt.hist(sponsor_types, bins=range(len(set(sponsor_types)) + 1), edgecolor='black')
        plt.title('Sponsor Types Distribution')
        plt.xlabel('Industry')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.savefig('static/sponsor_types.png')
    elif not(sponsor_types):
        plt.clf()
        plt.text(0.5, 0.5,'No Sponsor')
        plt.title('No Data')
        plt.xlabel('Industry') 
        plt.ylabel('Frequency')
        plt.xticks([])
        plt.yticks(np.arange(0, 1, step=1))
        
        plt.tight_layout()
        plt.savefig('static/sponsor_types.png')

    if campaign_statuses:
        plt.clf()
        plt.hist(campaign_statuses, bins=range(len(set(campaign_statuses)) + 1), edgecolor='black')
        plt.title('Campaign Statuses Distribution')
        plt.xlabel('Status')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.savefig('static/campaign_statuses.png')
    elif not(campaign_statuses):
        plt.clf()
        plt.text(0.5, 0.5,'No Campaign')
        plt.title('No Data')
        plt.xlabel('Status') 
        plt.ylabel('Frequency')
        plt.yticks(np.arange(0, 1, step=1))        
        plt.xticks([])
        plt.tight_layout()
        plt.savefig('static/campaign_statuses.png')
    if ad_request_statuses:
        plt.clf()
        plt.hist(ad_request_statuses, bins=range(len(set(ad_request_statuses)) + 1), edgecolor='black')
        plt.title('Ad Request Statuses Distribution')
        plt.xlabel('Status')
        plt.ylabel('Frequency')
        plt.xticks(rotation=45)
        plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout()
        plt.savefig('static/ad_request_statuses.png')
    elif not(ad_request_statuses):
        plt.clf()
        plt.text(0.5, 0.5,'No Ad Request')
        plt.title('No Data')
        plt.xlabel('Status') 
        plt.ylabel('Frequency')
        plt.xticks([])
        plt.yticks(np.arange(0, 1, step=1))
        plt.tight_layout()
        plt.savefig('static/ad_request_statuses.png')
    return render_template('admin_stats_dashboard.html')

@app.route("/sponsor_camp_dashboard/<int:sponsor_id>",methods=["GET","POST"])
def sponsor_camp_dashboard(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    if not sponsor:
        return "Sponsor not found"
    user = User.query.get(sponsor.id)
    if not user:
        return "User details not found"
    username = user.username
    
    search_query = request.form.get('search', '')
    if search_query:
        campaigns = Add_campaign.query.filter(
            Add_campaign.sponsor_id == sponsor_id,
            Add_campaign.title.ilike(f'%{search_query}%')
        ).all()
    else:
        campaigns = Add_campaign.query.filter(Add_campaign.sponsor_id == sponsor_id).all()
    return render_template("sponsor_camp_dashboard.html", campaigns=campaigns, 
    u_name=username, 
    sponsor_id=sponsor_id)

#flag user
@app.route('/flag_user/<int:user_id>', methods=['GET',"POST"])
def flag_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return 'User does not exist', 404
    
    user.flag = True
    db.session.commit()
    return redirect(f'/view_user/{user_id}')

@app.route('/unflag_user/<int:user_id>', methods=['GET',"POST"])
def unflag_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return 'User does not exist', 404
    
    user.flag = False
    db.session.commit()
    return redirect(f'/view_user/{user_id}')


#view user
@app.route('/view_user/<int:user_id>')
def view_user(user_id):
    user = User.query.get(user_id)
    current_user = User.query.filter_by(username=session.get('username')).first()
    if not user:
        return 'User not found'
    return render_template('view_user.html', user=user, current_user=current_user)

#send ad req
@app.route('/send_request/<int:influencer_id>', methods=['GET','POST'])
def send_request(influencer_id):
    current_user = User.query.filter_by(username=session.get('username')).first()
    if not(current_user):
        return 'current user not identified'
    if current_user.type.lower() == 'influencer':
        return ('You are not authorized to make this request.')
    campaigns = Add_campaign.query.filter_by(sponsor_id=current_user.id).all()
    if request.method== 'POST':
        sponsor_id = current_user.id
        campaign_id = request.form.get('campaign_id')
        messages = request.form.get('msg')
        requirements = request.form.get('req')
        pay = request.form.get('pay')
        status = request.form.get('status')
        if not sponsor_id:
            return 'Sponsor ID is missing.'
        if not influencer_id:
            return 'Influencer ID is missing.'
        ad_request = Ad_request(
        influencer_id=influencer_id,
        sponsor_id=sponsor_id,
        campaign_id=campaign_id,
        messages=messages,
        requirements=requirements,
        pay=pay,
        status=status)
        db.session.add(ad_request)
        db.session.commit()
        return redirect(f'/details_req/{ad_request.id}')   
    return render_template('send_req.html', influencer_id=influencer_id, sponsor_id=current_user.id, campaigns=campaigns)
    
#contracts
@app.route("/add_campaign/<int:sponsor_id>",methods=["GET","POST"])
def add_campaign(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    if request.method=="POST":
        title = request.form.get('title')
        description = request.form.get('descrip')
        niche = request.form.get('niche')
        s_date = request.form.get('startdate')
        e_date = request.form.get('enddate')
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        status = request.form.get('status')
        goals = request.form.get('goals')
        file = request.files.get('img')

        ALLOWED_EXTENSIONS = {'png'}
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        image_filename = None
        if file and allowed_file(file.filename):
            image_filename = f"campaign_{title.replace(' ', '_')}.{file.filename.rsplit('.', 1)[1].lower()}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            file.save(file_path)
        elif file:
            return "Invalid file type", 400

        new_campaign = Add_campaign(
            sponsor_id=sponsor.id, 
            title=title, 
            image=image_filename,
            description=description, 
            niche=niche, 
            s_date=s_date, 
            e_date=e_date, 
            budget=budget, 
            visibility=visibility, 
            goals=goals)
        db.session.add(new_campaign)
        db.session.commit()

        return redirect(f'/sponsor_camp_dashboard/{sponsor.id}')
    return render_template("add_campaign.html", action='Add', sponsor_id=sponsor_id , name=sponsor.name)
    
@app.route("/ad_request/<int:campaign_id>",methods=["GET","POST"])
def ad_request(campaign_id):
    campaign = Add_campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found", 404
    if campaign.flag:
        return 'Campaign is Flagged. You Can NOT make new request.'
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return "Sponsor not found"
    if request.method=="POST" and not(campaign.flag): 
        i_username = request.form.get('i_username')
        messages = request.form.get('msg')
        requirements = request.form.get('req')
        pay = request.form.get('pay')
        status = request.form.get('status')

        i_username = i_username.strip()
        
        user_i = User.query.filter_by(username=i_username.lower()).first()
        if (not user_i) or (user_i.type != 'influencer'):
            return 'influencer not Found'
        influencer_id = user_i.id
        sponsor_id = sponsor.id
        
        new_ad_request = Ad_request(
            campaign_id=campaign.id, 
            influencer_id=influencer_id,
            sponsor_id=sponsor_id, 
            messages=messages,
            requirements=requirements,
            pay=pay, 
            status=status)

        db.session.add(new_ad_request)
        db.session.commit()
        return redirect(f'/view_req/{campaign.id}')
    return render_template("ad_request.html",
    campaign=campaign,campaign_id=campaign.id,action='Add')

#buttons for camp 

@app.route('/view_campaign/<int:campaign_id>',methods=["GET","POST"])
def view_campaign(campaign_id):
    campaign = Add_campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found"
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return "Sponsor not found"
    return render_template('view_campaign.html', campaign=campaign, u_name=sponsor.name, sponsor=sponsor)

@app.route('/remove_campaign/<int:campaign_id>',methods=["GET","POST"])
def remove_campaign(campaign_id):
    campaign = Add_campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found or Deleted Succesfuly"
    sponsor_id = campaign.sponsor_id
    db.session.delete(campaign)
    db.session.commit()
    return redirect(f'/view_user/{sponsor_id}') 

#flag
@app.route('/flag_campaign/<int:campaign_id>',methods=["GET","POST"])
def flag_campaign(campaign_id):
    campaign = Add_campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found"
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return "Sponsor not found"
    name=sponsor.name

    campaign.flag = True
    db.session.commit()
    return redirect(f'/view_campaign/{campaign.id}') 

@app.route('/unflag_campaign/<int:campaign_id>',methods=["GET","POST"])
def unflag_campaign(campaign_id):
    campaign = Add_campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found"
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return "Sponsor not found"
    name=sponsor.name
    
    campaign.flag = False
    db.session.commit()
    return redirect(f'/view_campaign/{campaign.id}') 

@app.route('/update_campaign/<int:campaign_id>',methods=["GET","POST"])
def update_campaign(campaign_id):
    campaign = Add_campaign.query.get(campaign_id)
    if not campaign:
        return "Campaign not found"
    sponsor = Sponsor.query.get(campaign.sponsor_id)
    if not sponsor:
        return "Sponsor not found"
    name=sponsor.name
    if request.method == 'POST':
        campaign.description = request.form.get('descrip')
        campaign.niche = request.form.get('niche')
        campaign.s_date = request.form.get('startdate')
        campaign.e_date = request.form.get('enddate')
        campaign.budget = request.form.get('budget')
        campaign.visibility = request.form.get('visibility')
        campaign.status = request.form.get('status')
        campaign.goals = request.form.get('goals')
        file = request.files.get('img')

        ALLOWED_EXTENSIONS = {'png'}
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        if file and allowed_file(file.filename):
            image_filename = f"campaign_{campaign.title}.png"
            image_filename = secure_filename(image_filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            campaign.image = image_filename

        db.session.commit()
        return redirect(f'/view_campaign/{campaign.id}')

    return render_template('update_campaign.html', action= 'Update',campaign_id=campaign_id,
    sponsor=sponsor,name=name,
    title=campaign.title,
    descrip=campaign.description,
    img=campaign.image,
    niche=campaign.niche,
    startdate=campaign.s_date,
    enddate=campaign.e_date,
    budget=campaign.budget,
    visibility=campaign.visibility,
    status=campaign.status,
    goals=campaign.goals,
    sponsor_id=sponsor.id) 

#ad_req buttons
@app.route('/view_req/<int:campaign_id>' ,methods=["GET", "POST"])
def view_req(campaign_id):
    campaign=Add_campaign.query.get(campaign_id)
    current_user = User.query.filter_by(username=session.get('username')).first()
    if not(campaign):
        return 'Campaign does not exist'
    
    ad_requests = Ad_request.query.filter_by(campaign_id=campaign_id).all() 
    i_ids = {ad_request.influencer_id for ad_request in ad_requests}
    s_ids = {ad_request.sponsor_id for ad_request in ad_requests}
    
    influencers = User.query.filter(User.id.in_(i_ids)).all()
    sponsors = User.query.filter(User.id.in_(s_ids)).all()
    
    influencer_users = {}
    sponsor_users = {}
    
    for user in influencers:
        influencer_users[user.id] = user.username
    for user in sponsors:
        sponsor_users[user.id] = user.username

    return render_template('view_req.html',ad_requests=ad_requests,campaign=campaign,current_user=current_user, 
    influencer_users=influencer_users,sponsor_users=sponsor_users)


@app.route('/update_req/<int:ad_request_id>', methods=['GET', 'POST'])
def update_ad_request(ad_request_id):
    ad_request = Ad_request.query.get(ad_request_id)
    if not ad_request:
        return 'Ad Request does not exist', 404
    current_user = User.query.filter_by(username=session.get('username')).first()
    campaign= Add_campaign.query.get(ad_request.campaign_id)
    if not campaign:
        return 'Campaign does not exist', 404

    influencer = User.query.get(ad_request.influencer_id)
    sponsor = User.query.get(ad_request.sponsor_id)
    
    influencer_username = influencer.username if influencer else 'Unknown'
    sponsor_username = sponsor.username if sponsor else 'Unknown'
    if not(current_user):
        return 'Current user not identified'

    if current_user and (current_user.type == 'sponsor' or current_user.type == 'admin'):
        if request.method == 'POST':
            ad_request.influencer_id = influencer.id if influencer else ad_request.influencer_id
            ad_request.messages = request.form.get('msg')
            ad_request.requirements = request.form.get('req')
            ad_request.pay = request.form.get('pay')
            ad_request.status = request.form.get('status')
            db.session.commit()
            return redirect(f'/details_req/{ad_request_id}')
    
    elif current_user and current_user.type == 'influencer':
        # Influencers can only update the messages field
        if request.method == 'POST':
            ad_request.messages = request.form.get('msg')
            if current_user.id == ad_request.influencer_id:
                ad_request.pay = request.form.get('pay')
            db.session.commit()
            return redirect(f'/details_req/{ad_request_id}')
    return render_template('update_req.html', ad_request=ad_request, action='Update', campaign=campaign,
    influencer_username=influencer_username,sponsor_username=sponsor_username)

@app.route('/remove_req/<int:ad_request_id>', methods=['GET','POST'])
def remove_ad_request(ad_request_id):
    ad_request = Ad_request.query.get_or_404(ad_request_id)
    campaign_id = ad_request.campaign_id
    current_user = User.query.filter_by(username=session.get('username')).first()
    if not current_user:
        return 'User not found'
    if current_user.type.lower() in ['sponsor', 'admin']:
        db.session.delete(ad_request)
        db.session.commit()
    else:
        return 'You are not authorized to delete this ad request'
    return redirect(f'/view_campaign/{campaign_id}')

@app.route('/details_req/<int:ad_request_id>')
def details_req(ad_request_id):
    ad_request = Ad_request.query.get(ad_request_id)
    if not ad_request:
        return "Ad Request not found"
    i_id = ad_request.influencer_id
    s_id = ad_request.sponsor_id
    
    influencer = User.query.filter_by(id = i_id).first()
    sponsor = User.query.filter_by(id = s_id).first()
    
    influencer_username = influencer.username if influencer else 'Unknown'
    sponsor_username = sponsor.username if sponsor else 'Unknown'
    
    return render_template('details_req.html', ad_request=ad_request, 
    influencer_username=influencer_username,
    sponsor_username=sponsor_username)

@app.route('/accept_req/<int:ad_request_id>', methods=['GET','POST'])
def accept_req(ad_request_id):
    ad_request = Ad_request.query.get_or_404(ad_request_id)
    if (ad_request.status == 'Pending' or ad_request.status == 'Rejected'):
        ad_request.status = 'Accepted'
        db.session.commit()
    return redirect(f'/details_req/{ad_request_id}')

@app.route('/reject_req/<int:ad_request_id>', methods=['GET','POST'])
def reject_req(ad_request_id):
    ad_request = Ad_request.query.get_or_404(ad_request_id)
    if (ad_request.status == 'Pending' or ad_request.status == 'Accepted') :
        ad_request.status = 'Rejected'
        db.session.commit()
    return redirect(f'/details_req/{ad_request_id}')

#search
@app.route("/sponsor_find_dashboard/<int:sponsor_id>",methods=["GET","POST"])
def sponsor_find_dashboard(sponsor_id):
    sponsor= Sponsor.query.get(sponsor_id)
    if not sponsor:
        return 'sponsor not found'
    user= User.query.get(sponsor.id)
    if not user:
        return 'user not found'
    username= user.username
    if request.method=="POST":
        search = request.form.get('search')
        if search.isdigit():
            search_query = int(search)
            lower_bound = search_query - 10
            upper_bound = search_query + 10
            influencers = Influencer.query.filter(
                (Influencer.flw.between(lower_bound, upper_bound))
            ).all()
        else:
            search_pattern = f"%{search}%"
            influencers = Influencer.query.filter(
                ((User.username.ilike(search_pattern)) & (User.type=='influencer')) | #OR
                (Influencer.niche.ilike(search_pattern)) | #Case-insensitive search: ilike
                (Influencer.category.ilike(search_pattern)) |
                (Influencer.name.ilike(search_pattern))
            ).all()
    else: 
        influencers=[]
    return render_template("sponsor_find_dashboard.html",u_name=username,influencers=influencers, sponsor_id=sponsor_id)

@app.route("/influencer_find_dashboard/<int:influencer_id>",methods=["GET","POST"])
def influencer_find_dashboard(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return "Influencer not found"
    user = User.query.get(influencer.id)
    if not user:
        return "User details not found"
    username = user.username
    if request.method=="POST":
        search = request.form.get('search')
        search_pattern = f"%{search}%"
        campaigns = Add_campaign.query.filter(
            ((Add_campaign.title.ilike(search_pattern)) |
            (Add_campaign.niche.ilike(search_pattern)) |
            (Add_campaign.description.ilike(search_pattern)) )&
            (Add_campaign.visibility.ilike('%public%'))
            ).all()
    else: 
        campaigns=[]
    return render_template("influencer_find_dashboard.html",u_name=username,campaigns=campaigns, influencer_id=influencer_id)

#stats
@app.route("/influencer_stats_dashboard/<int:influencer_id>",methods=["GET","POST"])
def influencer_stats_dashboard(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if not influencer:
        return "Influencer not found"
    user = User.query.get(influencer.id)
    if not user:
        return "User details not found"
    username = user.username

    campaigns = []
    ad_requests = []
    campaigns_id = set()

    ad_requests = Ad_request.query.filter_by(influencer_id=influencer.id).all()
    accepted_count = 0
    pending_count = 0
    rejected_count = 0
    for request in ad_requests:
        if request.status == 'Accepted':
            accepted_count += 1
        elif request.status == 'Pending':
            pending_count += 1
        elif request.status == 'Rejected':
            rejected_count += 1
    num_ad_requests = len(ad_requests)

    campaign_ids = {req.campaign_id for req in ad_requests}
    public_campaigns = Add_campaign.query.filter(Add_campaign.id.in_(campaign_ids), Add_campaign.visibility == 'public').all()
    
    ad_request_statuses = [req.status for req in ad_requests]
    niche = [camp.niche for camp in public_campaigns]
    num_pc=len(niche)

    plt.clf()
    plt.hist(ad_request_statuses, bins=range(len(set(ad_request_statuses)) + 1), edgecolor='black')
    plt.title('Ad request Status')
    plt.xlabel('Status')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.ylim(bottom=0)
    y_ticks = np.arange(0, plt.ylim()[1] + 1, 1)
    plt.yticks(y_ticks)
    plt.tight_layout()
    plt.savefig('static/ad_req_status_influencer.png')
    
    plt.clf()
    plt.hist(niche, bins=range(len(set(niche)) + 1), edgecolor='black')
    plt.title('Campaign Niche Distribution')
    plt.xlabel('Niche')
    plt.ylabel('Frequency')
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.xticks(rotation=45)
    plt.ylim(bottom=0)
    y_ticks = np.arange(0, plt.ylim()[1] + 1, 1)
    plt.yticks(y_ticks)
    plt.tight_layout()
    plt.savefig('static/campaign_niche_influencer.png')

    return render_template('influencer_stats_dashboard.html',influencer_id=influencer_id, 
    influencer=influencer,
    campaigns=campaigns, campaigns_id=campaigns_id,ad_requests=ad_requests,
    username=username,
    num_ad_requests=num_ad_requests,
    accepted_count=accepted_count,
    pending_count=pending_count,
    rejected_count=rejected_count, public_campaigns=public_campaigns)

@app.route("/sponsor_stats_dashboard/<int:sponsor_id>", methods=["GET", "POST"])
def sponsor_stats_dashboard(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)

    campaigns = Add_campaign.query.filter_by(sponsor_id=sponsor_id).all()
    
    types = [campaign.niche for campaign in campaigns]
    visibility = [campaign.visibility for campaign in campaigns]

    plt.clf()
    plt.hist(types)
    plt.title('Campaign Types Distribution')
    plt.xlabel('Types')
    plt.ylabel('Frequency')
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.ylim(bottom=0)
    y_ticks = np.arange(0, plt.ylim()[1] + 1, 1)
    plt.yticks(y_ticks)
    plt.savefig('static/sponsor_campaign_types.png')

    plt.clf()
    plt.hist(visibility)
    plt.title('Campaign Visibility Distribution')
    plt.xlabel('Visibility')
    plt.ylabel('Frequency')
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.ylim(bottom=0)
    y_ticks = np.arange(0, plt.ylim()[1] + 1, 1)
    plt.yticks(y_ticks)
    plt.savefig('static/sponsor_campaign_visibility.png')

    return render_template('sponsor_stats_dashboard.html',sponsor_id=sponsor_id,campaigns=campaigns)
    
