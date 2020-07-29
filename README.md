# dc_power_meter
simple web app using Flask and Arduino

Arduino will read analog port A0,A1 & A2 and will calculate Voltage and
Current, this info is then sent to pc via serial communication using Json.

Flask gathers the info and shows it using AJAX, this information is sent to
Cloud Firestore and the last 6 entries of the database are shown in Homepage.

'/Database' url will fetch all the data stored on firestore for that
particular day (day can be changed), with this information, we get average,
maximum, and minimum values and show every value plotted using chartJS.

