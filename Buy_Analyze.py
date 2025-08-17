from Dependencies import *
print(list(csv_map.keys()))
max_prices={"Buy_Reform":1.2,"Buy_New":2.5,"Buy_Chalet":2.3,"Buy_Old":2.4}
# Pr/SqM => Recycle 1.5-2.1, Old 2.2-2.4, New 2.6-3.3, Chalet 1.6-2.1
k='Buy_Chalet'
df=pd.read_csv(csv_map[k])
print('Shapes:',df.shape)
inspect_dataframe(df)
df=prepare_data(df).drop('Price/room',axis=1)
print('Shapes:',df.shape)
print(df.head())

# Describe
round(df.describe(),1)
count_per_loc(df,k)
locs=mean_by_location(df,'Price/SqM')
filter_per_loc(df,'Barcelona').sort_values('Price/SqM')
#filter_by_string(df,'Link','105326563')

# Filtering Rows via individual criteria (use max_prices[k])
excl_locs=['Vilafranca del Penedès']
fil_row=filter_buy_rows(df,min_h=2,min_price_sqm=1.1,max_price_sqm=2.5,min_area_any=70,min_area_large=100,min_hab_large=2,max_size=130,exclude=excl_locs).sort_values(['Area','Price/SqM'])#.drop('Hab',axis=1)
print(len(fil_row),'\n',fil_row)
locs=mean_by_location(fil_row,'Price/SqM')
filter_per_loc(fil_row,'Vilafranca del Penedès')
df[df['Price/SqM']<2.1].sort_values('Area')


# Analysis Data
boxplot_location_groups(df)
print_df_by_var(df,['Price (€)', 'Area', 'Price/SqM'],k)
plot_price_vs_size(df,k+' => Price vs Size','Price','Area')
plot_price_vs_size(df,k+' => Price/Sqm vs Size','Price/SqM','Area')
plot_histogram(df,k,'Price/SqM')
plot_correlation_heatmap(df, ['Price', 'Area', 'Price/SqM'],k)



