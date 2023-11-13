
import requests
cv2_image = cv2.cvtColor(np.array(cam.raw_image), cv2.COLOR_RGB2BGR)
b,g,r = cv2.split(cv2_image)
array = g

dim_x = len(array[0])
dim_y = len(array)
print(dim_x, dim_y)
cropped_image = g[100:180, 100:200] #first is y direction, second is x
cam.show(cropped_image)

count_greater_than_50 = 0
count_smaller_than_or_equal_50 = 0

# Iterate through the 2D array
for row in cropped_image:
    for value in row:
        if value > 50:
            count_greater_than_50 += 1
        else:
            count_smaller_than_or_equal_50 += 1

#print('count greater than 50: ', count_greater_than_50, 'count less than 50: ', count_smaller_than_or_equal_50)
print("\n")

color = ''

if(count_greater_than_50 > count_smaller_than_or_equal_50):
    color = 'Green'
    print(color)
else:
    color = 'Red'
    print(color)


AirTOKEN = "patpid0u4zKgSSFLx.a1eb213d9be25990bc8954c37f2122c04fb8d93a934b741033ff1ac6154aaa2a"

url = "https://api.airtable.com/v0/appvKT35VLaa4hxIj/Color Table" #new url -- modified and re-shared Airtable
headers = {"Authorization": "Bearer " + AirTOKEN, "Content-Type":"application/json"}

json_data = {
    'records': [
        {
            'id': 'recJ6Ii0dsF2HulWg',
            'fields': {
                'Color Measure': color,
            },
        },
    ],
}

try:
    response = requests.patch('https://api.airtable.com/v0/appvKT35VLaa4hxIj/Color%20Table', headers=headers, json=json_data) #id reference code from Airtable API Website
    print("Successful post")
except:
    print(response.status_code)
