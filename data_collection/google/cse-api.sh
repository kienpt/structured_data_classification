HOST="cse.google.com"

EMAIL="ml2016nyu@gmail.com"
PASSWORD="Poly2018"
USERID="012281429458316433205"
CSEID="t_yb_yvquey"


URL="https://$HOST/api/$USERID/cse/$CSEID"
ISPOST=1

AUTHTOKEN=`curl -k https://www.google.com/accounts/ClientLogin -d Email=$EMAIL \
 -d Passwd=$PASSWORD -d accountType=GOOGLE -d service=cprose | grep -x "Auth=.*"`
echo "asdfasdfasdfddddddd"
echo $AUTHTOKEN
AUTHTOKEN=`echo $AUTHTOKEN | cut -d = -f 2`
AUTHTOKEN='AIzaSyBEUQhzDMwMEFNrws8hjMICqeBlGfnNapE'
AUTHTOKEN='ya29..zAJFsLGJ4iOqu22HWE-d1pz9ukYEgIlHULnovDt_WLVY3XYslQunKUgKtmWqvvzwIw'
AUTHHEADER="Authorization: Bearer $AUTHTOKEN"

TMP="post.xml"
echo "" > $TMP
XML='
<?xml version="1.0" encoding="UTF-8" ?>
<CustomSearchEngine id="t_yb_yvquey" creator="012281429458316433205" language="en" encoding="UTF-8" enable_suggest="true">
  <Title>Machine Learning</Title>
  <Context>
    <BackgroundLabels>
      <Label name="_cse_t_yb_yvquey" mode="BOOST" />
      <Label name="_cse_exclude_t_yb_yvquey" mode="ELIMINATE" />
    </BackgroundLabels>
  </Context>
  <LookAndFeel nonprofit="false" element_layout="8" theme="7" text_font="Arial, sans-serif" url_length="full" element_branding="show" enable_cse_thumbnail="true" promotion_url_length="full">
    <Logo />
    <Colors url="#008000" background="#FFFFFF" border="#FFFFFF" title="#0000CC" text="#000000" visited="#0000CC" title_hover="#0000CC" title_active="#0000CC" />
    <Promotions title_color="#0000CC" title_visited_color="#0000CC" url_color="#008000" background_color="#FFFFFF" border_color="#336699" snippet_color="#000000" title_hover_color="#0000CC" title_active_color="#0000CC" />
    <SearchControls input_border_color="#D9D9D9" button_border_color="#666666" button_background_color="#CECECE" tab_border_color="#E9E9E9" tab_background_color="#E9E9E9" tab_selected_border_color="#FF9900" tab_selected_background_color="#FFFFFF" />
    <Results border_color="#FFFFFF" border_hover_color="#FFFFFF" background_color="#FFFFFF" background_hover_color="#FFFFFF" ads_background_color="" ads_border_color="" />
  </LookAndFeel>
  <AdSense />
  <EnterpriseAccount />
  <ImageSearchSettings enable="false" />
  <autocomplete_settings />
  <sort_by_keys label="Relevance" key="" />
  <sort_by_keys label="Date" key="date" />
  <cse_advance_settings enable_speech="true" />
  <schema_org_schemas>Recipe</schema_org_schemas>
</CustomSearchEngine>'

echo $XML >> $TMP;

echo "Posting to $URL"
echo "Header: $AUTHHEADER"
echo "Content:"
cat $TMP

curl -v -X POST -d @$TMP -H "$AUTHHEADER" -H "Content-Type:text/xml" $URL
