package main

import (
	"fmt"
	"net/http"
	"net/url"
	"reflect"
	"strconv"
	"strings"

	"github.com/spf13/viper"
)

func send_data(ToNum string, message string) string {
	accountSid := viper.GetString("accountSid")
	authToken := viper.GetString("authToken")
	urlStr := viper.GetString("urlStr") + accountSid + "/Messages.json"

	msgData := url.Values{}
	msgData.Set("To", ToNum)
	msgData.Set("From", viper.GetString("fromNumber"))
	msgData.Set("Body", message)
	msgDataReader := *strings.NewReader(msgData.Encode())

	client := &http.Client{}
	req, _ := http.NewRequest("POST", urlStr, &msgDataReader)
	req.SetBasicAuth(accountSid, authToken)
	req.Header.Add("Accept", "application/json")
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")

	resp, _ := client.Do(req)
	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		return "SMS sent"
	} else {
		return resp.Status
	}
}

// validate To Phone Number is 10 digits long and contains only numbers
func validate_num(ToNum string) string {
	length := len(ToNum)
	i, err := strconv.Atoi(ToNum)
	if reflect.TypeOf(i).String() == "int" && length == 10 {
		return "valid"
	} else if err != nil {
		return "confirm phone number contains only numbers"
	} else {
		return "check phone number length"
	}
}

func main() {
	viper.SetConfigName("config") // name of config file (without extension)
	viper.AddConfigPath(".")      // path to look for the config file in
	err := viper.ReadInConfig()   // Find and read the config file
	if err != nil {               // Handle errors reading the config file
		panic(fmt.Errorf("Fatal error config file: %s \n", err))
	}

	fmt.Printf("Starting My History Day SMS service")

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "Welcome from My History Day SMS Service")
	})

	http.HandleFunc("/send", func(w http.ResponseWriter, r *http.Request) {
		r.ParseForm()
		validated := validate_num(r.FormValue("ToNumber"))
		if validated == "valid" {
			i := send_data(r.FormValue("ToNumber"), r.FormValue("Message"))
			if i == "SMS sent" {
				w.Write([]byte("SMS sent"))
			} else {
				http.Error(w, "Error sending SMS: "+i, 500)
			}
		} else {
			http.Error(w, "Error with To Number: "+validated, 400)
		}
	})

	http.ListenAndServe(viper.GetString("appUrl"), nil)
}
