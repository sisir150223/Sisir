import pandas as pd

df = pd.read_csv("ESG_Employee.csv")

#print(df)

df1 = df.dtypes
df2 = df.columns
df3 = str(df2)+str(df1)

print(df3)


with open("data_new_90","w") as file:file.write(df3+ "\n")

#data = df_30.to_csv("C:\\Users\\Sisir\\Desktop\\Data_finall.txt",index=False)

#print(data)

#with open("df_final_90", 'w') as totxt_file:totxt_file.write("\n".join(df3))

'''df_col = pd.read_csv("df_21.csv")
print(df_col)
df_col2 = pd.read_csv("new3.txt")
print(df_col2)

df_all_rows = pd.concat([df_col, df_col2], ignore_index=True)
print(df_all_rows)'''

#df_all = pd.concat([df_col, df5])
#print(df_all)

#data = df_all.to_csv("C:\\Users\\Sisir\\Desktop\\new_all2.txt",index=False)



#df_new = pd.concat([df, df_t], axis=0)

#print(df_new)



#df.loc[len(df.index)] = [df5]

#print(df)

#df = df.append(df5, ignore_index=True)

#print(df)

#df = pd.concat([df5, df]).reset_index(drop = True)
#print(df.T)new_row = pd.DataFrame({'Courses':'Hyperion', 'Fee':24000, 'Duration':'55days', 'Discount':1800}, index=[0])
