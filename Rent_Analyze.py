from Dependencies import *
pd.set_option('display.max_colwidth', None)
print(list(csv_map.keys()))
max_prices={"Rent_New":1.2,"Rent_Old":1.2}
# 1d 1.2, 1h 0.6 
k='Rent_Old'
df=pd.read_csv(csv_map[k]).assign(**{'Price (€)': lambda df: df['Price (€)'].astype(str).str.replace('€/mes', '', regex=False).str.strip()})
print('Shapes:',df.shape)
inspect_dataframe(df)
df=prepare_data(df).drop('Price/SqM',axis=1)
print('Shapes:',df.shape)

# Describe
round(df.describe(),1)
count_per_loc(df,k)
locs=mean_by_location(df,'Price/room')
filter_per_loc(df,'Barcelona').sort_values('Price/room')
filter_by_string(df,'Link','99454089')


# Filtering Rows via individual criteria
exc_loc=['Terrassa','Mataró','Sabadell','Martorell','Sant Vicenç de Montalt','Cabrera de Mar']
filt_old=filter_rent_rows(df,mx_pr_1h=1.2,mx_pr_room=0.7,min_area_1h=55,min_area_2h=70,min_area_3h=90,exclude=[]).sort_values(['Hab','Area','Price'])#.drop('Location',axis=1)
print(filt_old,'\n\nLength',len(filt_old))
#filter_by_string(filt_old,'Link','99454089')
#print_by_group(filt_old,'Location')


# Analysis Data
boxplot_location_groups(df,y_col='Price')
print_df_by_var(df,['Price', 'Area', 'Price/room'],k)
plot_price_vs_size(df,k+' => Price vs Size','Price','Area')
plot_price_vs_size(df,k+' => Price/room vs Hab','Price/room','Hab')
plot_price_vs_size(df,k+' => Price/room vs Size','Price/room','Area')
plot_histogram(df,k,'Price/room')
plot_histogram(df,k,'Price')
plot_histogram(df,k,'Area')
plot_correlation_heatmap(df,['Price', 'Area', 'Hab', 'Price/room'],k)

