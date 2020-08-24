import streamlit as st
import warnings
warnings.simplefilter("ignore", UserWarning)
import warnings
warnings.filterwarnings('ignore')
import pandas as pd 
import numpy as np 


st.title("Welcome to Talent Supply Pool")
st.subheader("Please select method for request submission")

#Read file
Skill=pd.read_excel('Data.xlsx',sheet_name='Skill_Tree', header=0,na_filter=True)
Supply=pd.read_excel('Data.xlsx',sheet_name='Supply', header=0,na_filter=True)
# Handling Data Issue handling
Skill['Sub Unit 3'].fillna(Skill['Sub Unit 2'],inplace=True)
Skill['Skill'].fillna(Skill['Sub Unit 3'],inplace=True)
Skill['Sub Unit 2']=Skill['Sub Unit 2'].str.replace('Managemnt','Management')
#Skill data handling
#Lookup creator
Skill['word']=Skill['Skill'].apply(lambda x: x.split(' '))
## Removing repetative and redundant words from lookup column
ind=0
changes=0
for i in Skill['word']:
    for j in i:
        if j=='Requirement' or j=='requirement':
            break
        elif j=='analysis':
            Skill.iloc[ind]['word']=Skill.iloc[ind]['word'].remove('analysis')
            changes=changes+1
        elif j=='Analysis':
            Skill.iloc[ind]['word']=Skill.iloc[ind]['word'].remove('Analysis')
            changes=changes+1
        elif j=='management':
            Skill.iloc[ind]['word']=Skill.iloc[ind]['word'].remove('management')
            changes=changes+1
        elif j=='Management':
            Skill.iloc[ind]['word']=Skill.iloc[ind]['word'].remove('Management')
            changes=changes+1
    ind=ind+1
#Update skill tree with new keywords from Discrepancy set
Skill_mod=Skill.copy()
index=Skill_mod.index.get_loc(Skill_mod.index[Skill_mod['Skill']=='Machine Learning'][0])
Skill_mod.iloc[index][5]=Skill_mod.iloc[index][5]+['ML']+['Artificial']+['Intelligence']
index=Skill_mod.index.get_loc(Skill_mod.index[Skill_mod['Skill']=='Advanced Excel'][0])
Skill_mod.iloc[index][5]=Skill_mod.iloc[index][5]+['VBA']
index=Skill_mod.index.get_loc(Skill_mod.index[Skill_mod['Skill']=='Presentation Skills'][0])
Skill_mod.iloc[index][5]=Skill_mod.iloc[index][5]+['Documentation']
index=Skill_mod.index.get_loc(Skill_mod.index[Skill_mod['Skill']=='Effective Communication'][0])
Skill_mod.iloc[index][5]=Skill_mod.iloc[index][5]+['Dashboarding']
HTML=[['Unit1','Technology','Web Technologies','Web development','HTML5',['HTML']]]
Taxation=[['Unit 5','Finance','Process','Accounting','Taxation',['Tax']]]
Skill_mod=Skill_mod.append(pd.DataFrame(HTML,columns=list(Skill_mod.columns)))
Skill_mod=Skill_mod.append(pd.DataFrame(Taxation,columns=list(Skill_mod.columns)))
Skill=Skill_mod.copy()

# Supply dataset
# Handle duplicates
Supply.drop_duplicates(subset=None, keep='first', inplace=True)
Supply['Sub Unit 1']=Supply['Sub Unit 1'].str.replace('Basic','Process')
Supply['Sub Unit 2']=Supply['Sub Unit 2'].str.replace('Managemnt','Management')
Supply['Sub Unit 2'].fillna(Supply['Skill'],inplace=True) # fill with skill if available
Supply['Sub Unit 2'].fillna(Supply['Sub Unit 1'],inplace=True) # fill rest with Unit 1
Supply['Sub Unit 3'].fillna(Supply['Skill'],inplace=True) # fill with skill if available
Supply['Sub Unit 3'].fillna(Supply['Sub Unit 2'],inplace=True)
Supply['Skill']=Supply['Skill'].str.replace('Cloud','AWS')
Supply['Skill']=Supply['Skill'].str.replace('Accounting','Revenue Management')
Supply['Skill']=Supply['Skill'].str.replace('Methodologies','Iterative')
Supply['Skill']=Supply['Skill'].str.replace('Operations','Finance operational reporting')
Supply['Skill']=Supply['Skill'].str.replace('Reporting','Management Reporting')
Supply['Skill']=Supply['Skill'].str.replace('Scripting','Python')
Supply['Skill']=Supply['Skill'].str.replace('Windows Servers','Administration')
Supply['Skill']=Supply['Skill'].str.replace('Management Management Reporting','Management Reporting')
Supply['Skill'].fillna(Supply['Sub Unit 3'],inplace=True)

#Supply master
Supply_master=Supply[['Name/ID','Years of experience', 'Rank', 'Service Line',
                       'Sub Service Line', 'SMU', 'Country', 'City', 'Bench Ageing (weeks)']]
Supply_master.drop_duplicates(subset='Name/ID', keep='first', inplace=True)
#Scoring system
Factors=['Bench Ageing','Exp','Functional skill','Location','Process skill','Rank','Technical skill']
SVCL1=[0,0.1,0.3,0.3,0.1,0.1,0.1]
SVCL2=[0.1,0.1,0.25,0.4,0.05,0,0.1]
SVCL3=[0.3,0.2,0.2,0.1,0.05,0,0.15]

Weightage=pd.DataFrame(Factors,columns=['Factor'])#,SVCL1,SVCL2,SVCL3)
Weightage['SVCL1']=SVCL1
Weightage['SVCL2']=SVCL2
Weightage['SVCL3']=SVCL3

#Bench Age
BAlist=list(Supply['Bench Ageing (weeks)'].unique())
BAlist=list(map(int,BAlist))
BAlist.sort(reverse=True)
BA=pd.DataFrame(BAlist,columns=['BA_values'])
step=Supply['Bench Ageing (weeks)'].nunique()
BA['weight']=list(np.linspace(0.5,1.0,step))

def BA_score(index):
    emp_BA=Supply_master.loc[index,'Bench Ageing (weeks)']
    score=round(float(BA[BA['BA_values']==emp_BA]['weight']),2)
    return score

def loc_score(req_city,req_Country,emp_city,emp_Country):
    score=0.0
    if req_city==emp_city:
        score=1.0
    elif req_Country==emp_Country:
        score=0.5
    return score

def exp_score(req_min_exp,emp_exp):
    if emp_exp>=req_min_exp:
        step=1/(Supply_master[Supply_master['Years of experience']>=(req_min_exp-1)]['Years of experience'].nunique()-1)
        score=list(np.arange(0.0,1.1,step))
        exp_list=list(map(int,list(Supply_master[Supply_master['Years of experience']>=(req_min_exp-1)]['Years of experience'].unique())))
        exp_list.sort(reverse=False)
        index=exp_list.index(emp_exp)
        return score[index]
    else:
        return 0

def rank_score(req_rank,emp_rank):
    reqvalue=int(req_rank.replace('Rank_',''))
    empvalue=int(emp_rank.replace('Rank_',''))
    diff=abs(reqvalue-empvalue)
    score=1.0-(diff*0.25)
    return score

#skill level score
Supply_skill=Supply[['Name/ID','Skill','Skill Level']]
Supply_skill['Skill Level']=Supply_skill['Skill Level'].replace(1,0.5)
Supply_skill['Skill Level']=Supply_skill['Skill Level'].replace(2,0.68)
Supply_skill['Skill Level']=Supply_skill['Skill Level'].replace(3,0.84)
Supply_skill['Skill Level']=Supply_skill['Skill Level'].replace(4,1.0)

#Supply_skill.to_excel('SupplySkill.xlsx')

def skill_score(emp,req_skill):
    tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==req_skill)].tolist()
    if len(tech1ind)>0:
        tech1ind=tech1ind[0]
        skillscore=Supply_skill.loc[tech1ind,'Skill Level']
        return skillscore
    else:
        return 0

def indivscore(rank,exp,SVCL,SubSVCL,SMU,city,country,Tech1,Tech2,Tech3,Func1,Func2,Func3,Proc1,Proc2,Proc3):
    Score2=pd.DataFrame([],columns=['Employee','score_nonskill','score_skill','total_score',
                                    'ServiceLine','SubSvcLine','SMU'])
    ctr2=0
    Req_rank=rank
    req_min_exp=exp
    req_city = city
    req_Country = country


    ## weights of each factor for SVC Line
    req_SVC=SVCL
    req_SVC=req_SVC.replace('ServiceLine','SVCL')
    rankw=Weightage.loc[5,req_SVC]
    expw=Weightage.loc[1,req_SVC]
    locw=Weightage.loc[3,req_SVC]
    BAw=Weightage.loc[0,req_SVC]
    funcW=Weightage.loc[2,req_SVC]
    techW=Weightage.loc[6,req_SVC]
    procW=Weightage.loc[4,req_SVC]
    
    for j in Supply_master.index:
        emp_rank=Supply_master.loc[j,'Rank']
        rankscore=rank_score(Req_rank,emp_rank)
        rankscore=rankscore*rankw
        #print(Supply_master.loc[j,'Name/ID'],"rank:",Req_rank,emp_rank)

        emp_exp=Supply_master.loc[j,'Years of experience']
        #print(Supply_master.loc[j,'Name/ID'],"exp:",req_min_exp,emp_exp)
        expscore=round(exp_score(req_min_exp,emp_exp),1)
        expscore=expscore*expw
        

        emp_city=Supply_master.loc[j,'City']
        emp_Country=Supply_master.loc[j,'Country']
        locscore=loc_score(req_city,req_Country,emp_city,emp_Country)
        locscore=locscore*locw

        BAscore=BA_score(j)
        BAscore=BAscore*BAw
        
        emp=Supply_master.loc[j,'Name/ID']
        techc=0
        funcc=0
        procc=0
        Tech1s=Tech2s=Tech3s=Func1s=Func2s=Func3s=Proc1s=Proc2s=Proc3s=0
        
        if Tech1 != 'N/A':
            Tech1s=skill_score(emp,Tech1)
            techc=techc+1
            
        if Tech2 != 'N/A':
            Tech2s=skill_score(emp,Tech2)
            techc=techc+1
            
        if Tech3 != 'N/A':
            Tech3s=skill_score(emp,Tech3)
            techc=techc+1
            
   
        if techc>0:
            techs=((Tech1s+Tech2s+Tech3s)/techc)*techW
        else:
            techs=0
            
        if Func1 != 'N/A':
            Func1s=skill_score(emp,Func1)
            funcc=funcc+1
        if Func2 != 'N/A':
            Func2s=skill_score(emp,Func2)
            funcc=funcc+1
        if Func3 != 'N/A':
            Func3s=skill_score(emp,Func3)
            funcc=funcc+1
        
        if funcc>0:
            funcs=((Func1s+Func2s+Func3s)/funcc)*funcW
        else:
            funcs=0
            
        if Proc1 != 'N/A':
            Proc1s=skill_score(emp,Proc1)
            procc=procc+1
        if Proc2 != 'N/A':
            Proc2s=skill_score(emp,Proc2)
            procc=procc+1
        if Proc3 != 'N/A':
            Proc3s=skill_score(emp,Proc3)
            procc=procc+1
        
        if procc>0:
            procs=((Proc1s+Proc2s+Proc3s)/procc)*procW
        else:
            procs=0
        
        total_score_non_skill=round((rankscore+expscore+locscore+BAscore),2)
        total_score_skill=round((techs+funcs+procs),2)

        
        SVCscore=0
        Subsvcscore=0
        SMUscore=0
        
        if Supply_master.loc[j,'Service Line']==SVCL:
            SVCscore=1
        if Supply_master.loc[j,'Sub Service Line']==SubSVCL:
            Subsvcscore=1
        if Supply_master.loc[j,'SMU']==SMU:
            SMUscore=1
        
        #Create DataFrame
        Score2.loc[ctr2,'score_nonskill']=total_score_non_skill
        Score2.loc[ctr2,'score_skill']=total_score_skill
        Score2.loc[ctr2,'Employee']=emp
        Score2['total_score']=Score2['score_nonskill']+Score2['score_skill']
        
        Score2.loc[ctr2,'ServiceLine']=SVCscore
        Score2.loc[ctr2,'SubSvcLine']=Subsvcscore
        Score2.loc[ctr2,'SMU']=SMUscore
        
        Score2['total_score']=Score2['total_score'].apply(lambda x:round(x,2))
        Score2=Score2.sort_values(by=['ServiceLine','SubSvcLine','SMU','total_score'],ascending=False)
        
        ctr2=ctr2+1
        
    return Score2

###################################################################################
###################################### Bulk Load ###################################
if st.checkbox("Bulk Upload",False):
    #import io
    #file_buffer = st.file_uploader(...)
    #text_io = io.TextIOWrapper(file_buffer)
    uploaded_file = st.file_uploader("Choose the demand Excel file", type="xlsx")
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        #st.write(data)
        st.set_option('deprecation.showfileUploaderEncoding', False)
        Demand=data
    #Demand Data Issue handling - Drop rows with all nan
        Demand.dropna(axis=0,how='all',inplace=True)
        Demand_tmp=Demand.copy()
        cols=['Technical Skill 1','Technical Skill 2','Technical Skill 3','Functional Skill 1',
              'Functional Skill 2','Functional Skill 3',
              'Process Skill 1','Process Skill 2','Process Skill 3']
        discrepancy=[]
        for col in cols:
            Demand_tmp[col]=Demand_tmp[col].str.replace(' ', '')
            for i in Demand_tmp.index:
                for col in cols:
                    flag=0
                    for j in list(Skill['Skill']):
                        if(str(Demand[col][i]).find(j)!=-1):
                            flag=1
                            break
                    if flag==1:
                        Demand_tmp[col][i]=str(Demand[col][i])
                    else:
                        flag2=0
                        ind=-1
                        for j in list(Skill['word']):
                            ind = ind+1
                            for k in j:
                                if(str(Demand_tmp[col][i]).find(k)!=-1):
                                    flag2=1
                                    Demand_tmp[col][i]=str(Skill.iloc[ind,4])
                                    break
                        if flag2==0:
                            discrepancy.append(str(Demand_tmp[col][i]))
                            Demand_tmp[col][i]="N/A"
        discrepancy_set=list(set(discrepancy)) 
        if len(discrepancy_set)>2:
            st.write("Found discrepancy in the following skills. Please correct and submit")
            st.write(discrepancy)
        else:
            Score=pd.DataFrame([],columns=['Request','Employee','score_nonskill','score_skill','total_score',
                                           'ServiceLine','SubSvcLine','SMU'])
            ctr=0
            for i in Demand_tmp.index:
                Req_rank=Demand_tmp.loc[i,'Rank']
                req_min_exp=Demand_tmp.loc[i,'Min Experience']
                req_city = Demand_tmp.loc[i,'Location ']
                req_Country = Demand_tmp.loc[i,'Country']
                req_SubSVC=Demand_tmp.loc[i,'Requestor Sub ServiceLine']
                req_SMU=Demand_tmp.loc[i,'Requestor SMU']
                
                ## weights of each factor for SVC Line
                req_SVC=Demand_tmp.loc[i,'Requestor Service Line']
                req_SVC=req_SVC.replace('ServiceLine','SVCL')
                rankw=Weightage.loc[5,req_SVC]
                expw=Weightage.loc[1,req_SVC]
                locw=Weightage.loc[3,req_SVC]
                BAw=Weightage.loc[0,req_SVC]
            
                for j in Supply_master.index:
                    emp_rank=Supply_master.loc[j,'Rank']
                    rankscore=rank_score(Req_rank,emp_rank)
                    rankscore=rankscore*rankw
            
                    emp_exp=Supply_master.loc[j,'Years of experience']
                    expscore=round(exp_score(req_min_exp,emp_exp),1)
                    expscore=expscore*expw
                    
            
                    emp_city=Supply_master.loc[j,'City']
                    emp_Country=Supply_master.loc[j,'Country']
                    locscore=loc_score(req_city,req_Country,emp_city,emp_Country)
                    locscore=locscore*locw
            
                    BAscore=BA_score(j)
                    BAscore=BAscore*BAw
            
                    total_score=round((rankscore+expscore+locscore+BAscore),2)
                    
                    SVCscore=0
                    Subsvcscore=0
                    SMUscore=0
                    
                    if Supply_master.loc[j,'Service Line']==Demand_tmp.loc[i,'Requestor Service Line']:
                        SVCscore=1
                    if Supply_master.loc[j,'Sub Service Line']==req_SubSVC:
                        Subsvcscore=1
                    if Supply_master.loc[j,'SMU']==req_SMU:
                        SMUscore=1
                        
                    Score.loc[ctr,'score_nonskill']=total_score
                    Score.loc[ctr,'Employee']=Supply_master.loc[j,'Name/ID']
                    Score.loc[ctr,'Request']=Demand_tmp.loc[i,'Requestor']
                    Score.loc[ctr,'ServiceLine']=SVCscore
                    Score.loc[ctr,'SubSvcLine']=Subsvcscore
                    Score.loc[ctr,'SMU']=SMUscore
                    
                    ctr=ctr+1
            #Skill scorer
            pd_ctr=0
            for ind in Demand_tmp.index:
                req_SVC=Demand_tmp.loc[ind,'Requestor Service Line']
                req_SVC=req_SVC.replace('ServiceLine','SVCL')
                techW=Weightage.loc[6,req_SVC]
                
                for emp in Supply_skill['Name/ID'].unique():
                    score=0
                    tech1s=tech2s=tech3s=0
                    counter=0
                    if Demand_tmp.loc[ind,'Technical Skill 1'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Technical Skill 1'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            tech1s=skillscore
                        counter=counter+1
                            
                    if Demand_tmp.loc[ind,'Technical Skill 2'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Technical Skill 2'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            tech2s=skillscore
                        counter=counter+1
                            
                    if Demand_tmp.loc[ind,'Technical Skill 3'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Technical Skill 3'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            tech3s=skillscore
                        counter=counter+1
                            
                    if counter>0:
                        score=round(((tech1s+tech2s+tech3s)/counter)*techW,2)
                    else:
                        score=0
                    #score=round(score*techW,2)
                    
                    Score.loc[pd_ctr,'score_skill']=score
                    pd_ctr=pd_ctr+1
            
            #Functional skill
            pd_ctr=0
            for ind in Demand_tmp.index:
                req_SVC=Demand_tmp.loc[ind,'Requestor Service Line']
                req_SVC=req_SVC.replace('ServiceLine','SVCL')
                funcW=Weightage.loc[2,req_SVC]
                
                for emp in Supply_skill['Name/ID'].unique():
                    score=0
                    counter=0
                    if Demand_tmp.loc[ind,'Functional Skill 1'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Functional Skill 1'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            score=score+skillscore
                        counter=counter+1
                            
                    
                    if Demand_tmp.loc[ind,'Functional Skill 2'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Functional Skill 2'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            score=score+skillscore
                        counter=counter+1
                            
                    if Demand_tmp.loc[ind,'Functional Skill 3'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Functional Skill 3'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            score=score+skillscore
                        counter=counter+1
                    if counter>0:
                        score=round(score/counter,2)
                    else:
                        score=score
                    score=round(score*funcW,2)
                    
                    FuncScore=score
                    Score.loc[pd_ctr,'score_skill']=Score.loc[pd_ctr,'score_skill']+score
                    
                    pd_ctr=pd_ctr+1
            
            #Process skill
            pd_ctr=0
            for ind in Demand_tmp.index:
                req_SVC=Demand_tmp.loc[ind,'Requestor Service Line']
                req_SVC=req_SVC.replace('ServiceLine','SVCL')
                procW=Weightage.loc[4,req_SVC]
                
                for emp in Supply_skill['Name/ID'].unique():
                    score=0
                    counter=0
                    if Demand_tmp.loc[ind,'Process Skill 1'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Process Skill 1'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            score=score+skillscore
                        counter=counter+1
                    
                    if Demand_tmp.loc[ind,'Process Skill 2'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Process Skill 2'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            score=score+skillscore
                        counter=counter+1
                            
                    if Demand_tmp.loc[ind,'Process Skill 3'] != 'N/A':
                        tech1ind=Supply_skill.index[(Supply_skill['Name/ID']==emp)&(Supply_skill['Skill']==Demand_tmp.loc[ind,'Process Skill 3'])].tolist()
                        if len(tech1ind)>0:
                            tech1ind=tech1ind[0]
                            skillscore=Supply_skill.loc[tech1ind,'Skill Level']
                            score=score+skillscore
                        counter=counter+1
                        
                    if counter>0:
                        score=round(score/counter,2)
                    else:
                        score=score
                    score=round(score*procW,2)
                    
                    ProcScore=score
                    Score.loc[pd_ctr,'score_skill']=round((Score.loc[pd_ctr,'score_skill']+score),2)
                    
                    pd_ctr=pd_ctr+1
    # FInal display
            
            Score['total_score']=Score['score_nonskill']+Score['score_skill']
            Score['total_score']=Score['total_score'].apply(lambda x:round(x,2))
            #Score=Score.sort_values(by=['total_score','SMU','SubSvcLine','ServiceLine'],ascending=False)
            Score=Score.sort_values(by=['ServiceLine','SubSvcLine','SMU','total_score'],ascending=False)
    
            st.subheader("Input requests")
            st.write(Demand_tmp)
            Request = st.slider("Request selector",1, Demand_tmp['Requestor'].nunique())
            ReqID="Req_"+str(Request)
            st.subheader("Employee wise data")
            st.write(Score[Score['Request']==ReqID])

    
##########################################################################
############# Individual Request Submission ##############################

else:
    Req=st.text_input('Request ID',value='Req_1')
    Rank=st.text_input('Rank',value='Rank_1')
    Exp=st.text_input('Minimum Experience',value='8')
    City=st.text_input('City',value='Bangalore')
    Country=st.text_input('Country',value='India')
    SVCL=st.text_input('Service Line',value='ServiceLine3')
    SubSVCL=st.text_input('Sub Service Line',value='SubserviceLine4')
    SMU=st.text_input('SMU','SMU2')
    
    Tech1=st.text_input('Technical Skill 1',value='Advanced Excel')
    Tech2=st.text_input('Technical Skill 2',value='Microsoft Office')
    Tech3=st.text_input('Technical Skill 3',value='N/A')       
    Func1=st.text_input('Functional Skill 1',value='Enterprise Risk Analysis')
    Func2=st.text_input('Functional Skill 2',value='Requirement Analysis')
    Func3=st.text_input('Functional Skill 3',value='Account Management')
    Proc1=st.text_input('Process Skill 1',value='Effective Communication')
    Proc2=st.text_input('Process Skill 2',value='Presentation Skills')
    Proc3=st.text_input('Process Skill 3',value='Team Play')
    
    flag=1    
    if not Req:
        st.write("Missing Request")
        flag=0
    elif not Rank:
        st.write("Missing Rank")
        flag=0
    elif not Exp:
        st.write("Missing Experience")
        flag=0
    elif not City:
        flag=0
        st.write("Missing City")
    elif not Country:
        flag=0
        st.write("Missing Country")
    elif not SVCL:
        flag=0
        st.write("Missing Service Line")
        
    if flag==1: 
        st.subheader("Talent pool score based for given Request")
        st.write("REQUEST NUMBER: ", Req)
        Score2=pd.DataFrame()
        Score2=indivscore(Rank,int(Exp),SVCL,SubSVCL,SMU,City,Country,Tech1,Tech2,Tech3,Func1,Func2,Func3,Proc1,Proc2,Proc3)
        st.write(Score2)
