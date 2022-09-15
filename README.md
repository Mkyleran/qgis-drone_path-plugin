Drone Path plugin Document:

This plugin creates a FlyLitchi compatible csv file with way points for the drone. It requires an input polygon and an input line from the user. The csv file has all the mandatory columns with default values to open in FlyLitchi mission hub. The plugin is in Vector category as shown below.
![image](https://user-images.githubusercontent.com/86660902/190371631-1e697b94-beb9-43d0-b3cd-efd6b7e77400.png)
 

Drone Path Plugin:
The Drone Path plugin opens with few default drone camera parameters which are editable. Drone image parameters are calculated based on these inputs. 
![image](https://user-images.githubusercontent.com/86660902/190371668-ffa8f3e3-5aec-45bf-a55b-4a0a77795c22.png)

 
The parameters and the input types for camera parameters are as described below.
Parameter	Description	Allowed Inputs
Altitude:	The user must input at what height the drone must fly over the area of interest.	Integer in meters. Two or three digits and no decimals allowed.
Overlap %:	Sidewise overlap in drone path.	Upto two digits and no decimals allowed
Field of View (FoV)	The observable view through the lens of the drone camera.	Enter degrees. Two or three digits and upto two decimal allowed.
Aspect ratio (r):	Drone image’s width to height ratio.	One digit and upto two decimals allowed.
Image height and Image Width:		Four or five digits and no decimals allowed.

Calculated parameters and formulae: 
Calculated parameters	Formulae
FoV (radians):	FoV(in degrees)*(3.14/180)
Diagonal:	2*(altitude)*tan((FoV)/2)
Side A (m):	D/(1+(r**2)) - square(r)

Side B (m): 	r * side A

Area of the image: 	side A * side B
Ground Sampling Distance (GSD)(m): 	square root(area/image width*image height)
Distance between gridlines(m):	(1-overlap%)*(image width)*GSD
Then the user has to upload a shapefile of the area of interest. This shapefile should be of polygon geometry type only and in EPSG:4326 GCS projection. Following the selection of AOI, the user must either draw or upload a line - ‘Input_line.shp’:

Notes on the line:
●	This line must be outside the AOI polygon.
●	It should be in a direction parallel to the desired drone path.
●	The drone path will be drawn to the right/above this line.
●	This line is plotted in EPSG:4326 GCS projection.

Example of input line and the drone path:  Input line                                  Drone path drawn above the input line 
This is the output csv file that can be imported into FlyLitchi Mission hub.
Workflow:
The ‘Calculate Gridlines’ button follows the below mentioned steps:
●	The parallel lines to the user defined ‘Input_line.shp’ are created using the ‘native:arrayoffsetlines’ tool of QGIS. This is a temporary shapefile and is added to the QGIS interface as ‘paralle_lines.shp’.
●	These lines are clipped to the boundary of the AOI shapefile. This is also a temporary shapefile and is added to the QGIS interface as ‘clipped_lines.shp’.
●	The vertices of the clipped lines are extracted which are the way points of the drone path. This is also a temporary shapefile and is added to the QGIS interface as ‘Way_Points.shp’.
●	The user must then specify the number of parallel lines required to cover the entire AOI. 
●	A Fly Litchi compatible csv file is then created and it can be opened in Fly Litchi Mission hub - Missions (Bottom left) - Import - Select the csv file - OK.
●	The waypoints in the csv file must show on the map view.




