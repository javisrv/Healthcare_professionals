#!/usr/bin/env python
# coding: utf-8

# # HEALTH PROFESSIONALS REGISTRY PROVINCE OF NEUQUEN

# # [1- Introduction](#1)
# 
# # [2- Loading basic libraries](#2)
# 
# # [3- Data frame loading](#3)
# 
# # [4- Cleaning and transformation](#4)
#  
#  - ## [A- professionals](#4.A)
#  - ## [B- licenses](#4.B)
#  - ## [C- Merge professionals and licenses](#4.C)
#  - ## [D- Check columns](#4.D)
#  - ## [E- Merge prof_lic and professions](#4.E)
#  - ## [F- Merge prof_lic_prof and specialties](#4.F)
#  - ## [G- Merge prof_lic_prof_spe and effector](#4.G)
#  - ## [H- Final transformations](#4.H)
# 
# # [5- Data analysis](#5)
# 
# # [6- Conclusion](#6)

# <a id='1'></a>
# 
# ---

# # 1. Introduction

# - The Federal Network of Health Professionals Records (REFEPS in spanish) covers the totality of health workers in Argentina, which is the articulation of the records of professionals from all provinces.
# 
# - The design of the file responds to the requirements established in the Ministerial Resolution 604/2005 of the Mercosur, which sets the minimum registration matrix for health professionals, with the objective of having harmonized basic information. This implies standardizing the information of health professionals who are registered in each province.
# 
# - The design and structuring of the data included in the form have been developed by the SISA team and approved by the Health Regulation Board and Health Services of the Ministry of Health of the Nation and by the network of health regulation referents and SISA technology.
# 
# - Each Provincial Health Ministry uploads its records of professionals, technicians and assistants to the system and articulates them. In this way, if you unify the different records that a professional may have, it can be found in the case that you have enrollments in more than a province, which has more than a profession.
# 
# - The following notebook is based on public data from the province of neuquén. If some data were incomplete, random data were generated in order to carry out the analysis.
# 
# - Source of data:
# http://datos.neuquen.gob.ar/dataset/salud/resource/348847e3-4f4c-4369-ac0c-d08cbfeda60f

# <a id='2'></a>
# 
# ---

# # 2. Loading basic libraries

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, date
import random
import folium
from folium.plugins import MarkerCluster
from branca.element import Figure


# <a id='3'></a>
# 
# ---

# # 3. Data frame loading

# In[2]:


professionals_directory = "professionals.csv"
licenses_directory = "licenses.csv" 
professions_directory = "professions.csv"
specialties_directory = "specialties.csv"
effector_directory = "effector.csv"


# In[3]:


professionals = pd.read_csv(professionals_directory, encoding = "latin1", delimiter = ";")
professionals.head(3)


# In[4]:


licenses = pd.read_csv(licenses_directory, encoding = "latin1", delimiter = ";")
licenses.head(1)


# In[5]:


professions = pd.read_csv(professions_directory, encoding = "latin1", delimiter = ";")
professions.head(3)


# In[6]:


specialties = pd.read_csv(specialties_directory, encoding = "latin1", delimiter = ";")
specialties.head(3)


# In[7]:


effector = pd.read_csv(effector_directory, encoding = "latin1", delimiter = ";")
effector.head(3)


# <a id='4'></a>
# 
# ---

# # 4. Cleaning and transformation

# <a id='4.A'></a>
# 
# ## A. professionals

# In[8]:


professionals["ProfesionalSexo"].unique()


# Creation of functions to search for missing data from the column `ProfesionalSexo` in other columns

# In[9]:


def search_genre_fem(dataframe, genre_col):
    for i in dataframe.index:
        index_fem = dataframe.at[i, genre_col] != "Femenino"
        if index_fem:
            for column in dataframe.columns:
                if (dataframe.at[i, column] == "Femenino"):
                    dataframe.loc[i, [genre_col, column]] = dataframe.loc[i, [column, genre_col]].values  
                    
    return dataframe


# In[10]:


professionals = search_genre_fem(professionals, "ProfesionalSexo")


# In[11]:


def search_genre_masc(dataframe, genre_col):
    for i in dataframe.index:
        index_masc = dataframe.at[i, genre_col] != "Masculino"
        if index_masc:
            for column in dataframe.columns:
                if (dataframe.at[i, column] == "Masculino"):
                    dataframe.loc[i, [genre_col, column]] = dataframe.loc[i, [column, genre_col]].values
                    
    return dataframe


# In[12]:


professionals = search_genre_masc(professionals, "ProfesionalSexo")


# In[13]:


professionals["ProfesionalSexo"].unique()


# Selection of columns of interest

# In[14]:


professionals_columns = ["ProfesionalDocumento", "ProfesionalApellido", "ProfesionalNombre",
                         "ProfesionalFechaNacimiento", "ProfesionalSexo"]


# In[15]:


professionals = professionals[professionals_columns]
professionals.head(3)


# In[16]:


professionals.shape


# <a id='4.B'></a>
# 
# ## B. licenses

# In[17]:


licenses_columns = ["ME_ProfesionalDocumento", "ME_ProfesionID", "ME_EspecialidadID", "ME_ProfesionalApellido", 
                    "ME_ProfesionalNombre", "ME_ProfesionEspecialidadMatric", "ME_EspecialidadMatAnio"]


# In[18]:


licenses = licenses[licenses_columns]


# In[19]:


licenses.isna().sum()


# In[20]:


licenses.head(3)


# In[21]:


licenses.shape


# <a id='4.C'></a>
# 
# ## C. Merge professionals and licenses

# In[22]:


prof_lic = licenses.merge(professionals, left_on = "ME_ProfesionalDocumento", right_on = "ProfesionalDocumento", how = "outer").reset_index()


# In[23]:


prof_lic.shape


# In[24]:


prof_lic.head(3)


# In[25]:


prof_lic.isna().sum()


# Replace nulls of the columns `ME_ProfesionalDocumento, ME_ProfesionalApellido, ME_ProfesionalNombre` with the values of the columns `ProfesionalDocumento, ProfesionalApellido, ProfesionalNombre` respectively

# In[26]:


columns_from_replace = ["ME_ProfesionalDocumento", "ME_ProfesionalApellido", "ME_ProfesionalNombre"]
columns_to_replace = ["ProfesionalDocumento", "ProfesionalApellido", "ProfesionalNombre"]
columns_zip = zip(columns_from_replace, columns_to_replace)

for f, t in columns_zip:
        prof_lic[f] = np.where(prof_lic[f].isna(), prof_lic[t], prof_lic[f])


# In[27]:


prof_lic.isna().sum()


# <a id='4.D'></a>
# 
# ## D. Check columns

# Creation of check columns to corroborate values of the columns of the dataframe `professionals/licenses`

# **ProfesionalApellido** column

# In[28]:


prof_lic_last = prof_lic.dropna(subset = ["ProfesionalApellido"])


# In[29]:


prof_lic_last["last_check"] = prof_lic_last["ME_ProfesionalApellido"] == prof_lic_last[ "ProfesionalApellido"]


# In[30]:


prof_lic_last.query("last_check == False")


# I can keep the column `ME_ProfesionalApellido`

# **ProfesionalDocumento** column

# In[31]:


prof_lic_doc = prof_lic.dropna(subset = ["ProfesionalDocumento"])


# In[32]:


prof_lic_doc["last_check"] = prof_lic_doc["ME_ProfesionalDocumento"] == prof_lic_doc[ "ProfesionalDocumento"]


# In[33]:


prof_lic_doc.query("last_check == False")


# I can keep the column `ME_ProfesionalDocumento`

# **Selection of columns to work**

# In[34]:


prof_lic.columns


# In[35]:


columns_prof_lic = ["ME_ProfesionalDocumento", "ME_ProfesionalApellido", "ME_ProfesionalNombre",
                    "ProfesionalFechaNacimiento", "ProfesionalSexo",
                    "ME_ProfesionID", "ME_EspecialidadID", "ME_ProfesionEspecialidadMatric", "ME_EspecialidadMatAnio"]

prof_lic = prof_lic[columns_prof_lic]


# In[36]:


prof_lic.head(3)


# <a id='4.E'></a>
# 
# ## E. idEfector column creation

# Since neither professionals.csv nor licenses.csv have a column with the effector id, the `idEfector`column is created fictitiously, with random numbers.

# In[37]:


effector_list = [1,2,3,4,5,6,7,8,9,10]
effector_size = prof_lic.shape[0]
effector_p = [0.2, 0.02, 0.03, 0.1, 0.1, 0.15, 0.20, 0.05, 0.10, 0.05]


# In[38]:


prof_lic["idEfector"] =  np.random.choice(effector_list, effector_size, p = effector_p)


# In[39]:


#prof_lic["idEfector"] = np.random.randint(low = 1, high = 11, size = prof_lic.shape[0], dtype = int)


# In[40]:


prof_lic.head()


# <a id='4.E'></a>
# 
# ## E. Merge prof_lic and professions

# In[41]:


prof_lic_prof = prof_lic.merge(professions[["ProfesionID", "ProfesionDescripcion"]], left_on = "ME_ProfesionID", right_on = "ProfesionID", how = "left").reset_index()


# In[42]:


prof_lic_prof.head(3)


# In[43]:


prof_lic_prof = prof_lic_prof.drop(["ME_ProfesionID"], axis = 1)


# In[44]:


prof_lic_prof.head(3)


# <a id='4.F'></a>
# 
# ## F. Merge prof_lic_prof and specialties

# In[45]:


prof_lic_prof_spe = prof_lic_prof.merge(specialties[["EspecialidadID", "EspecialidadDescripcion"]], left_on = "ME_EspecialidadID", right_on = "EspecialidadID", how = "left").reset_index()


# In[46]:


prof_lic_prof_spe.head()


# In[47]:


prof_lic_prof_spe = prof_lic_prof_spe.drop(["EspecialidadID"], axis = 1)


# In[48]:


prof_lic_prof_spe.head(3)


# <a id='4.G'></a>
# 
# ## G. Merge prof_lic_prof_spe and effector

# In[49]:


df_final = prof_lic_prof_spe.merge(effector[["idEfector", "nombre"]], on = "idEfector", how = "left")


# In[50]:


df_final.head()


# In[51]:


df_final = df_final.drop(["level_0", "index"], axis = 1)


# In[52]:


col_order = ["ME_ProfesionalDocumento", "ME_ProfesionalApellido", "ME_ProfesionalNombre", 
            "ProfesionalFechaNacimiento", "ProfesionalSexo", "ProfesionID", "ProfesionDescripcion",
            "ME_EspecialidadID", "EspecialidadDescripcion", "ME_ProfesionEspecialidadMatric", "ME_EspecialidadMatAnio",
            "idEfector", "nombre"]
df_final = df_final[col_order]


# In[53]:


df_final.head(3)


# <a id='4.H'></a>
# 
# ## H. Final transformations

# **Rename columns**

# In[54]:


df_final.columns


# In[55]:


df_final = df_final.rename(columns = {"ME_ProfesionalDocumento": "ID", 
                                      "ME_ProfesionalApellido": "Last_name",
                                      "ME_ProfesionalNombre": "Name",
                                      "ProfesionalFechaNacimiento": "Birth",
                                      "ProfesionalSexo": "Gender",
                                      "ProfesionID": "Profession_ID",
                                      "ProfesionDescripcion": "Profession",
                                      "EspecialidadDescripcion": "Specialty_ID",
                                      "ME_EspecialidadID": "Specialty",
                                      "ME_ProfesionEspecialidadMatric": "License_number",
                                      "ME_EspecialidadMatAnio": "License_year",
                                      "idEfector": "Effector_ID",
                                      "nombre": "Effector_name"})


# In[56]:


df_final.head(3)


# **Create age column**
# 
# Remember that the birth column has 1199 nulls

# In[57]:


df_final.dtypes


# In[58]:


df_final["Birth"] = pd.to_datetime(df_final["Birth"], infer_datetime_format = True)


# In[59]:


df_final.dtypes


# In[60]:


today = date.today()


# In[61]:


df_final["Age"] = df_final["Birth"].apply(lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)))


# In[62]:


df_final.head(3)


# **Aggregating random ages**

# First: selection of columns where "Age" == NaN

# In[63]:


nulls = df_final.loc[df_final["Age"].isna()]


# In[64]:


nulls.head()


# Second: Creation of null values by random values, giving greater weight to age range [25-34] and [35-44] 

# In[65]:


# 5% will have an age [23-24]
# 5% of 1199 is approximately 60 (because there are 1199 nulls)
nulls.loc[98:157, "Age"] = np.random.randint(low = 22, high = 25, size = 60, dtype = int)

# 15% will have an age [25-34]
# 15% of 1199 is approximately 178
nulls.loc[158:335, "Age"] = np.random.randint(low = 25, high = 35, size = 178, dtype = int)

# 25% will have an age [35-44]
# 25% of 1199 is approximately 300
nulls.loc[336:635, "Age"] = np.random.randint(low = 35, high = 45, size = 300, dtype = int)

# 30% will have an age [45-54]
# 30% of 1199 is approximately 364
nulls.loc[636:999, "Age"] = np.random.randint(low = 45, high = 55, size = 364, dtype = int)

# 15% will have an age [55-64]
# 15% of 1199 is approximately 178
nulls.loc[1000:1177, "Age"] = np.random.randint(low = 55, high = 65, size = 178, dtype = int)

# 15% will have an age [> 65]
# 15% of 1199 is approximately 178
nulls.loc[1178:, "Age"] = np.random.randint(low = 65, high = 80, size = 119, dtype = int)


# Third: pd.cut function to corroborate the proportions of each age group

# In[66]:


nulls["Age_range"] = pd.cut(x = nulls["Age"],
                            bins = [1, 24, 34, 44, 54, 64, np.inf],
                            labels=['-24', '25-34', '35-44','45-54', '55-64', '+65'])


# In[67]:


nulls["Age_range"].value_counts(normalize = True).sort_index()


# Fourth: replace null values with generated random values

# In[68]:


df_final.loc[df_final["Age"].isna(), "Age"] = nulls["Age"]


# **Create column "Age_range"**

# In[69]:


df_final["Age_range"] = pd.cut(x = df_final["Age"],
                            bins = [1, 24, 34, 44, 54, 64, np.inf],
                            labels=['-24', '25-34', '35-44','45-54', '55-64', '+65'])


# In[70]:


df_final.head(3)


# In[71]:


df_final.isna().sum()


# **Complete "Gender" column**

# In[72]:


gender_list = ["Masculino", "Femenino"]
gender_size = df_final.loc[df_final["Gender"].isna()].shape[0]
gender_p = [0.35, 0.65]


# In[73]:


df_final["Gender"].value_counts()


# In[74]:


df_final.loc[df_final["Gender"].isna(), "Gender"] = np.random.choice(gender_list, gender_size, p = gender_p)


# In[75]:


df_final["Gender"].value_counts()


# **Create lat and long columns**

# In[76]:


df_final["Effector_name"].value_counts()


# In[77]:


# Values of latitud latitude longitude from google maps

lajas = [-38.52048258094623, -70.36063117589912]
alumine = [-39.23546241878282, -70.91271328953913]
cholar = [-37.440626194651614, -70.64528074727662]
bouquet_roldan = [-38.95883938265797, -68.08537866071416]
burd = [-38.82102886575302, -68.137022973652]
junin = [-39.94850928019381, -71.076500396902]
del_valle = [-39.013402717636836, -68.42517068585245]
zapala = [-38.90205988682674, -70.0649764760577]
cuevas = [-38.07067985574281, -70.61521946628989]
chocon = [-39.26016797983336, -68.77677741042214]


# In[78]:


df_final.loc[df_final["Effector_name"] == "HOSPITAL LAS LAJAS", "Lat"] = -38.52048258094623
df_final.loc[df_final["Effector_name"] == "HOSPITAL LAS LAJAS", "Long"] = -70.36063117589912

df_final.loc[df_final["Effector_name"] == "HOSPITAL ALUMINE", "Lat"] = -39.23546241878282
df_final.loc[df_final["Effector_name"] == "HOSPITAL ALUMINE", "Long"] = -70.91271328953913

df_final.loc[df_final["Effector_name"] == "HOSPITAL EL CHOLAR", "Lat"] = -37.440626194651614
df_final.loc[df_final["Effector_name"] == "HOSPITAL EL CHOLAR", "Long"] = -70.64528074727662

df_final.loc[df_final["Effector_name"] == "HOSPITAL BOUQUET ROLDAN", "Lat"] = -38.95883938265797
df_final.loc[df_final["Effector_name"] == "HOSPITAL BOUQUET ROLDAN", "Long"] = -68.08537866071416

df_final.loc[df_final["Effector_name"] == "HOSPITAL DR. NATALIO BURD", "Lat"] = -38.82102886575302
df_final.loc[df_final["Effector_name"] == "HOSPITAL DR. NATALIO BURD", "Long"] = -68.137022973652

df_final.loc[df_final["Effector_name"] == "HOSPITAL JUNIN DE LOS ANDES", "Lat"] = -39.94850928019381
df_final.loc[df_final["Effector_name"] == "HOSPITAL JUNIN DE LOS ANDES", "Long"] = -71.076500396902

df_final.loc[df_final["Effector_name"] == "HOSPITAL SENILLOSA", "Lat"] = -39.013402717636836
df_final.loc[df_final["Effector_name"] == "HOSPITAL SENILLOSA", "Long"] = -68.42517068585245

df_final.loc[df_final["Effector_name"] == "HOSPITAL ZAPALA", "Lat"] = -38.90205988682674
df_final.loc[df_final["Effector_name"] == "HOSPITAL ZAPALA", "Long"] = -70.0649764760577

df_final.loc[df_final["Effector_name"] == "HOSPITAL DR. JOSE CUEVAS", "Lat"] = -38.07067985574281
df_final.loc[df_final["Effector_name"] == "HOSPITAL DR. JOSE CUEVAS", "Long"] = -70.61521946628989

df_final.loc[df_final["Effector_name"] == "HOSPITAL EL CHOCON", "Lat"] = -39.26016797983336
df_final.loc[df_final["Effector_name"] == "HOSPITAL EL CHOCON", "Long"] = -68.77677741042214


# In[79]:


df_final.head()


# In[80]:


df_final.isna().sum()


# Rows containing nulls in `profession` column are eliminated and only those professionals with `profession = MEDICO` are selected

# In[81]:


df_final = df_final.dropna(subset = ["Profession"])


# In[82]:


df_final["Profession"].unique() 


# In[83]:


df_final = df_final[df_final["Profession"] == "MEDICO"]
df_final["Profession"].unique()


# In[84]:


df_final.isna().sum()


# In[85]:


df_final.shape


# <a id='5'></a>
# 
# ---

# # 5. Data analysis

# In[86]:


df_final["Profession"].unique()


# In[87]:


femenine = df_final["Gender"].value_counts(normalize = True)[0]
masculine = df_final["Gender"].value_counts(normalize = True)[1]


# In[88]:


plt.style.use("seaborn-white")

# Creating plot
fig, ax = plt.subplots(figsize = (10, 7))
 
 
# Creating dataset
data = [(femenine * 100).round(2), (masculine * 100).round(2)]
labels = ["Femenine", "Masculine"]
explode = (0.1, 0) 

textprops = {"fontsize": 15}
_, _, autopcts = ax.pie(data, labels = labels, autopct = '%1.1f%%', pctdistance = 0.75, textprops = textprops,
                       shadow = False, startangle = 40, colors = ("darkseagreen", "skyblue"))

centre_circle = plt.Circle((0, 0), 0.55, fc = 'white')
fig = plt.gcf()
fig.gca().add_artist(centre_circle)

plt.setp(autopcts, **{'color':'white', 'weight':'bold', 'fontsize': 16})
plt.title("Gender proportion", position = (.465, 1), backgroundcolor = "steelblue", color = "white", fontsize = 20, weight = "bold")

plt.show()


# In[89]:


fig, ax = plt.subplots(figsize = (10, 8))

sns.boxplot(x = "Gender", y = "Age", data = df_final)

plt.title("Boxplot Age by Gender", fontsize = 20)
plt.xlabel("Gender",  fontsize = 18)
plt.ylabel("Age",  fontsize = 18)
plt.xticks(fontsize = 16)
plt.yticks(fontsize = 16)

plt.show()


# In[144]:


masc_median = df_final.loc[df_final["Gender"] == "Masculino", "Age"].median()
fem_median = df_final.loc[df_final["Gender"] == "Femenino", "Age"].median()

print(f"Median masculine gender: {masc_median}")
print(f"Median femenine gender {fem_median}")


# In[90]:


fig, ax = plt.subplots(figsize = (10, 8))

sns.countplot(x = "Age_range", data = df_final, hue = "Gender")

plt.title("Boxplot Age by Age range", fontsize = 20)
plt.xlabel("Age",  fontsize = 18)
plt.ylabel("Count",  fontsize = 18)
plt.xticks(fontsize = 16)
plt.yticks(fontsize = 16)
plt.legend(title = "Gender:", title_fontproperties = {"size": 16}, fontsize = 16)

plt.show()


# In[91]:


specialties_prop = df_final.groupby("Specialty_ID")[["License_number"]].count() / df_final.shape[0] * 100
specialties_prop = specialties_prop.sort_values("License_number", ascending = False).round(2)
specialties_prop                                                


# In[92]:


specialties_top10 = specialties_prop.head(10)
specialties_top10


# In[93]:


specialties_top10_sort = specialties_top10.sort_values("License_number", ascending = True)


# In[94]:


plt.style.use("seaborn-white")
fig, ax = plt.subplots(figsize = (10, 10))

ax.barh(specialties_top10_sort.index, specialties_top10_sort["License_number"], color = sns.color_palette("RdPu", 16), edgecolor = "black")

plt.ylabel("Specialty: \n", fontsize = 20)
plt.xlabel("\n Licenses by specialty (%)", fontsize = 18)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)
plt.title("Proportion of licenses by specialty \n", fontsize = 20)


plt.show()


# In[95]:


effector_prop = df_final.groupby("Effector_name")[["License_number"]].count() / df_final.shape[0] * 100
effector_prop = effector_prop.sort_values("License_number", ascending = False).round(2)
effector_prop                                                


# In[96]:


effector_prop_sort = effector_prop.sort_values("License_number", ascending = True)


# In[97]:


plt.style.use("seaborn-white")
fig, ax = plt.subplots(figsize = (10, 10))

ax.barh(effector_prop_sort.index, effector_prop_sort["License_number"], color = sns.color_palette("RdPu", 16), edgecolor = "black")

plt.ylabel("Specialty: \n", fontsize = 20)
plt.xlabel("\n Licenses by effector (%)", fontsize = 18)
plt.xticks(fontsize = 18)
plt.yticks(fontsize = 18)
plt.title("Proportion of licenses by effector \n", fontsize = 20)


plt.show()


# In[98]:


print(f"Number of dataframe rows prior to elminate duplicates: {df_final.shape[0]}.")
print(f"Number of duplicates based on the 'ID' column': {df_final['ID'].duplicated().sum()}.")


# In[99]:


df_final_withoutnulls = df_final.drop_duplicates(subset = "ID")
df_final_withoutnulls.shape


# In[100]:


pyramid = pd.DataFrame()

for i in df_final_withoutnulls["Age_range"].unique():
    mask_m = (df_final_withoutnulls["Age_range"] == i) & (df_final_withoutnulls["Gender"] == "Masculino")
    mask_f = (df_final_withoutnulls["Age_range"] == i) & (df_final_withoutnulls["Gender"] == "Femenino")
    pyramid = pyramid.append({"Age": i, "M": mask_m.sum() , "F": mask_f.sum()}, ignore_index = True)


# In[101]:


pyramid


# In[102]:


pyramid["M"] = pyramid["M"] / -1
pyramid["F"] = pyramid["F"] / 1


# In[103]:


ages = ['+65', '55-64', '45-54', '35-44', '25-34', '-24']


# In[104]:


fig, axes = plt.subplots(figsize = (14, 6))

ax1 = sns.barplot(x = "M", y = "Age", data = pyramid, order = ages, palette = "crest_r")
ax2 = sns.barplot(x = "F", y = "Age", data = pyramid, order = ages, palette = "flare_r")

plt.title("Medical professional population pyramid. \n", fontsize = 20)
plt.xlabel("Masculine / Femenine", fontsize = 18)
plt.ylabel("Age range \n", fontsize = 18)

plt.yticks(fontsize = 16)
plt.xticks(ticks = [-250, -200, -150, -100, -50, 0, 50, 100, 150, 200, 250], fontsize = 16)

plt.axvline(x = 0, color = "white")
plt.grid(axis = "x", linestyle = "--")

plt.show()


# In[134]:


location_data = df_final[["Effector_name", "Lat", "Long"]]


# In[146]:


fig = Figure(width = 500, height = 300)

neuquen_map = folium.Map(location = [location_data["Lat"].mean(),
                                 location_data["Long"].mean()],
                                 zoom_start = 7)
for (index, row) in location_data.iterrows():
    folium.Marker(location = [row.loc["Lat"], row.loc["Long"]], 
                  popup = row.loc["Effector_name"], 
                  tooltip = row.loc["Effector_name"]).add_to(neuquen_map)
fig.add_child(neuquen_map)
fig


# In[147]:


neuquen_map.save("neuquen_map.html")


# In[153]:


fig = Figure(width = 500, height = 300)

neuquen_map2 = folium.Map(location = [location_data["Lat"].mean(),
                                 location_data["Long"].mean()],
                                 zoom_start = 7)

marker_cluster = MarkerCluster().add_to(neuquen_map2)

for (index, row) in location_data.iterrows():
    folium.Marker(location = [row.loc["Lat"], row.loc["Long"]], popup = row.loc["Effector_name"]).add_to(marker_cluster) #popup = row.loc["Effector_name"]

fig.add_child(neuquen_map2)
fig


# In[149]:


neuquen_map2.save("neuquen_map2.html")


# <a id='6'></a>
# 
# ---

# # 6. Conclusion

# - In the analysis carried out, with some simulated data, it was possible to observe that 62% of medical professionals correspond to the female gender, with a median of 49 for the female gender and 46 for the male gender..
# 
# - It is observed that the majority of medical professionals are in the range of 35-54 years of age.
# 
# - On the basis of the number of enrollments (since a doctor may have more than one enrollment) the specialties of Pediatrics, Medicina del Trabajo and Clínica Mëdica are the ones that predominate.
# 
# - The effector with the largest number of licenses is the Hopsital Dr. Natalio Burd.
