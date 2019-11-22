Search.setIndex({docnames:["adding_new_slack_apps","api","autogen/manage","autogen/omnibot","autogen/omnibot.authnz","autogen/omnibot.callbacks","autogen/omnibot.routes","autogen/omnibot.scripts","autogen/omnibot.services","autogen/omnibot.services.slack","autogen/omnibot.utils","autogen/setup","autogen/tests","autogen/tests.integration","autogen/tests.unit","autogen/tests.unit.omnibot","autogen/tests.unit.omnibot.authnz","autogen/tests.unit.omnibot.services","autogen/tests.unit.omnibot.services.slack","configuration","contributing","development","event_parsing","index","installation","observability","receivers","slack_proxying","writing_new_callbacks"],envversion:{"sphinx.domains.c":1,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":1,"sphinx.domains.javascript":1,"sphinx.domains.math":2,"sphinx.domains.python":1,"sphinx.domains.rst":1,"sphinx.domains.std":1,sphinx:56},filenames:["adding_new_slack_apps.rst","api.rst","autogen/manage.rst","autogen/omnibot.rst","autogen/omnibot.authnz.rst","autogen/omnibot.callbacks.rst","autogen/omnibot.routes.rst","autogen/omnibot.scripts.rst","autogen/omnibot.services.rst","autogen/omnibot.services.slack.rst","autogen/omnibot.utils.rst","autogen/setup.rst","autogen/tests.rst","autogen/tests.integration.rst","autogen/tests.unit.rst","autogen/tests.unit.omnibot.rst","autogen/tests.unit.omnibot.authnz.rst","autogen/tests.unit.omnibot.services.rst","autogen/tests.unit.omnibot.services.slack.rst","configuration.rst","contributing.rst","development.rst","event_parsing.rst","index.rst","installation.rst","observability.rst","receivers.rst","slack_proxying.rst","writing_new_callbacks.rst"],objects:{"":{"/api/v1/slack/get_channel/(team_name)/(bot_name)/(channel_name)":[1,0,1,"get--api-v1-slack-get_channel-(team_name)-(bot_name)-(channel_name)"],"/api/v1/slack/get_ims/(team_name)/(bot_name)":[1,0,1,"get--api-v1-slack-get_ims-(team_name)-(bot_name)"],"/api/v1/slack/get_team/(team_name)":[1,0,1,"get--api-v1-slack-get_team-(team_name)"],"/api/v1/slack/get_user/(team_name)/(bot_name)/(email)":[1,0,1,"get--api-v1-slack-get_user-(team_name)-(bot_name)-(email)"],"/api/v1/slack/send_im/(team_name)/(bot_name)/(email)":[1,1,1,"post--api-v1-slack-send_im-(team_name)-(bot_name)-(email)"],"/api/v2/slack/action/(team_name)/(bot_name)":[1,1,1,"post--api-v2-slack-action-(team_name)-(bot_name)"],manage:[2,2,0,"-"],omnibot:[3,2,0,"-"],tests:[12,2,0,"-"]},"omnibot.authnz":{allowed_paths:[4,3,1,""],enforce_checks:[4,3,1,""],envoy_checks:[4,2,0,"-"]},"omnibot.authnz.envoy_checks":{envoy_internal_check:[4,3,1,""],envoy_permissions_check:[4,3,1,""]},"omnibot.callbacks":{interactive_component_callbacks:[5,2,0,"-"],message_callbacks:[5,2,0,"-"],network_callbacks:[5,2,0,"-"],slash_command_callbacks:[5,2,0,"-"]},"omnibot.callbacks.interactive_component_callbacks":{echo_dialog_submission_callback:[5,3,1,""]},"omnibot.callbacks.message_callbacks":{channel_channel_callback:[5,3,1,""],channel_response_callback:[5,3,1,""],congratulations_bot_callback:[5,3,1,""],example_attachment_callback:[5,3,1,""],example_topic_callback:[5,3,1,""],help_callback:[5,3,1,""],specials_callback:[5,3,1,""],test_callback:[5,3,1,""]},"omnibot.callbacks.network_callbacks":{http_callback:[5,3,1,""]},"omnibot.callbacks.slash_command_callbacks":{bigemoji_callback:[5,3,1,""],echo_callback:[5,3,1,""],tableflip_callback:[5,3,1,""],unfliptable_callback:[5,3,1,""]},"omnibot.processor":{parse_kwargs:[3,3,1,""],process_event:[3,3,1,""],process_interactive_component:[3,3,1,""],process_slash_command:[3,3,1,""]},"omnibot.routes":{api:[6,2,0,"-"]},"omnibot.routes.api":{get_bot_ims:[6,3,1,""],get_channel_by_name:[6,3,1,""],get_team_id_by_name:[6,3,1,""],get_user_v2:[6,3,1,""],healthcheck:[6,3,1,""],instrument_event:[6,3,1,""],queue_event:[6,3,1,""],send_bot_im:[6,3,1,""],slack_action_v2:[6,3,1,""],slack_event:[6,3,1,""],slack_interactive_component:[6,3,1,""],slack_slash_command:[6,3,1,""],verify_bot:[6,3,1,""]},"omnibot.scripts":{omniredis:[7,2,0,"-"],utils:[7,2,0,"-"]},"omnibot.scripts.omniredis":{PurgeRedis:[7,4,1,""]},"omnibot.scripts.omniredis.PurgeRedis":{run:[7,5,1,""]},"omnibot.scripts.utils":{CreateSQSQueue:[7,4,1,""]},"omnibot.scripts.utils.CreateSQSQueue":{run:[7,5,1,""]},"omnibot.services":{get_boto_client:[8,3,1,""],get_boto_session:[8,3,1,""],omniredis:[8,2,0,"-"],slack:[9,2,0,"-"],sqs:[8,2,0,"-"],stats:[8,2,0,"-"]},"omnibot.services.omniredis":{get_redis_client:[8,6,1,""]},"omnibot.services.slack":{bot:[9,2,0,"-"],client:[9,3,1,""],get_channel:[9,3,1,""],get_channel_by_name:[9,3,1,""],get_channels:[9,3,1,""],get_emoji:[9,3,1,""],get_groups:[9,3,1,""],get_im_channel_id:[9,3,1,""],get_ims:[9,3,1,""],get_mpims:[9,3,1,""],get_name_from_user:[9,3,1,""],get_user:[9,3,1,""],get_user_by_email:[9,3,1,""],get_user_by_name:[9,3,1,""],get_users:[9,3,1,""],interactive_component:[9,2,0,"-"],message:[9,2,0,"-"],parser:[9,2,0,"-"],slash_command:[9,2,0,"-"],team:[9,2,0,"-"],update_channel:[9,3,1,""],update_channels:[9,3,1,""],update_emoji:[9,3,1,""],update_group:[9,3,1,""],update_groups:[9,3,1,""],update_im:[9,3,1,""],update_ims:[9,3,1,""],update_mpim:[9,3,1,""],update_mpims:[9,3,1,""],update_user:[9,3,1,""],update_users:[9,3,1,""]},"omnibot.services.slack.bot":{Bot:[9,4,1,""],BotInitializationError:[9,7,1,""]},"omnibot.services.slack.bot.Bot":{bot_id:[9,5,1,""],get_bot_by_bot_id:[9,5,1,""],get_bot_by_name:[9,5,1,""],get_bot_by_verification_token:[9,5,1,""],interactive_component_handlers:[9,5,1,""],message_handlers:[9,5,1,""],name:[9,5,1,""],oauth_bot_token:[9,5,1,""],oauth_token:[9,5,1,""],slash_command_handlers:[9,5,1,""],team:[9,5,1,""],verification_token:[9,5,1,""]},"omnibot.services.slack.interactive_component":{InteractiveComponent:[9,4,1,""]},"omnibot.services.slack.interactive_component.InteractiveComponent":{action_ts:[9,5,1,""],actions:[9,5,1,""],bot:[9,5,1,""],callback_id:[9,5,1,""],channel:[9,5,1,""],channel_id:[9,5,1,""],component_type:[9,5,1,""],event_trace:[9,5,1,""],message:[9,5,1,""],parsed_channel:[9,5,1,""],parsed_user:[9,5,1,""],payload:[9,5,1,""],response_url:[9,5,1,""],submission:[9,5,1,""],team:[9,5,1,""],trigger_id:[9,5,1,""],user:[9,5,1,""]},"omnibot.services.slack.message":{Message:[9,4,1,""],MessageUnsupportedError:[9,7,1,""]},"omnibot.services.slack.message.Message":{bot:[9,5,1,""],bot_id:[9,5,1,""],channel:[9,5,1,""],channel_id:[9,5,1,""],channels:[9,5,1,""],command_text:[9,5,1,""],directed:[9,5,1,""],emails:[9,5,1,""],event_trace:[9,5,1,""],match:[9,5,1,""],match_type:[9,5,1,""],mentioned:[9,5,1,""],parsed_text:[9,5,1,""],payload:[9,5,1,""],set_match:[9,5,1,""],specials:[9,5,1,""],subtype:[9,5,1,""],team:[9,5,1,""],text:[9,5,1,""],thread_ts:[9,5,1,""],ts:[9,5,1,""],urls:[9,5,1,""],user:[9,5,1,""],users:[9,5,1,""]},"omnibot.services.slack.parser":{extract_channels:[9,3,1,""],extract_command:[9,3,1,""],extract_emails:[9,3,1,""],extract_emojis:[9,3,1,""],extract_mentions:[9,3,1,""],extract_specials:[9,3,1,""],extract_subteams:[9,3,1,""],extract_urls:[9,3,1,""],extract_users:[9,3,1,""],replace_channels:[9,3,1,""],replace_emails:[9,3,1,""],replace_specials:[9,3,1,""],replace_urls:[9,3,1,""],replace_users:[9,3,1,""],unextract_channels:[9,3,1,""],unextract_specials:[9,3,1,""],unextract_users:[9,3,1,""]},"omnibot.services.slack.slash_command":{SlashCommand:[9,4,1,""]},"omnibot.services.slack.slash_command.SlashCommand":{bot:[9,5,1,""],bot_id:[9,5,1,""],channel:[9,5,1,""],channel_id:[9,5,1,""],channels:[9,5,1,""],command:[9,5,1,""],emails:[9,5,1,""],enterprise_id:[9,5,1,""],enterprise_name:[9,5,1,""],event_trace:[9,5,1,""],parsed_text:[9,5,1,""],payload:[9,5,1,""],response_url:[9,5,1,""],specials:[9,5,1,""],team:[9,5,1,""],text:[9,5,1,""],trigger_id:[9,5,1,""],urls:[9,5,1,""],user_id:[9,5,1,""],users:[9,5,1,""]},"omnibot.services.slack.team":{Team:[9,4,1,""],TeamInitializationError:[9,7,1,""]},"omnibot.services.slack.team.Team":{get_team_by_id:[9,5,1,""],get_team_by_name:[9,5,1,""],name:[9,5,1,""],team_id:[9,5,1,""]},"omnibot.services.sqs":{get_client:[8,3,1,""],get_queue_url:[8,3,1,""]},"omnibot.services.stats":{get_statsd_client:[8,3,1,""]},"omnibot.settings":{get:[3,3,1,""]},"omnibot.utils":{get_callback_id:[10,3,1,""],settings:[10,2,0,"-"]},"omnibot.utils.settings":{bool_env:[10,3,1,""],float_env:[10,3,1,""],int_env:[10,3,1,""],str_env:[10,3,1,""]},"omnibot.watcher":{bootstrap:[3,3,1,""],main:[3,3,1,""],watch_channels:[3,3,1,""],watch_emoji:[3,3,1,""],watch_groups:[3,3,1,""],watch_ims:[3,3,1,""],watch_mpims:[3,3,1,""],watch_users:[3,3,1,""]},"omnibot.webhook_worker":{delete_message:[3,3,1,""],handle_message:[3,3,1,""],handle_messages:[3,3,1,""],main:[3,3,1,""],wait_available:[3,3,1,""]},"tests.conftest":{SettingsOverrider:[12,4,1,""],client:[12,3,1,""],settings:[12,3,1,""]},"tests.conftest.SettingsOverrider":{reset:[12,5,1,""]},"tests.unit":{omnibot:[15,2,0,"-"]},"tests.unit.omnibot":{authnz:[16,2,0,"-"],services:[17,2,0,"-"],settings_test:[15,2,0,"-"]},"tests.unit.omnibot.authnz":{authnz_test:[16,2,0,"-"],envoy_checks_test:[16,2,0,"-"]},"tests.unit.omnibot.authnz.authnz_test":{test_allowed_paths:[16,3,1,""],test_enforce_checks:[16,3,1,""]},"tests.unit.omnibot.authnz.envoy_checks_test":{test_envoy_internal_check:[16,3,1,""],test_envoy_permissions_check:[16,3,1,""]},"tests.unit.omnibot.services":{slack:[18,2,0,"-"]},"tests.unit.omnibot.services.slack":{bot_test:[18,2,0,"-"],interactive_component_test:[18,2,0,"-"],message_test:[18,2,0,"-"],parser_test:[18,2,0,"-"],team_test:[18,2,0,"-"]},"tests.unit.omnibot.services.slack.bot_test":{test_team:[18,3,1,""]},"tests.unit.omnibot.services.slack.interactive_component_test":{test_interactive_block_component:[18,3,1,""],test_interactive_component:[18,3,1,""]},"tests.unit.omnibot.services.slack.message_test":{test_message:[18,3,1,""]},"tests.unit.omnibot.services.slack.parser_test":{test_extract_user:[18,3,1,""],test_not_supported_extract:[18,3,1,""]},"tests.unit.omnibot.services.slack.team_test":{test_team:[18,3,1,""]},"tests.unit.omnibot.settings_test":{test_handlers:[15,3,1,""],test_primary_slack_bot:[15,3,1,""],test_slack_bot_tokens:[15,3,1,""],test_slack_teams:[15,3,1,""]},omnibot:{app:[3,2,0,"-"],authnz:[4,2,0,"-"],callbacks:[5,2,0,"-"],processor:[3,2,0,"-"],routes:[6,2,0,"-"],scripts:[7,2,0,"-"],services:[8,2,0,"-"],settings:[3,2,0,"-"],setup_logging:[3,2,0,"-"],utils:[10,2,0,"-"],watcher:[3,2,0,"-"],webhook_worker:[3,2,0,"-"],wsgi:[3,2,0,"-"]},tests:{conftest:[12,2,0,"-"],integration:[13,2,0,"-"],unit:[14,2,0,"-"]}},objnames:{"0":["http","get","HTTP get"],"1":["http","post","HTTP post"],"2":["py","module","Python module"],"3":["py","function","Python function"],"4":["py","class","Python class"],"5":["py","method","Python method"],"6":["py","attribute","Python attribute"],"7":["py","exception","Python exception"]},objtypes:{"0":"http:get","1":"http:post","2":"py:module","3":"py:function","4":"py:class","5":"py:method","6":"py:attribute","7":"py:exception"},terms:{"04939292775a6f4a1817e5e846c11609":22,"15s":25,"2f00b63":22,"2f66f9":22,"2f7fa9":22,"2fa":22,"2fava_0009":22,"2favatar":22,"2fdf10d":22,"2fimg":22,"3c989f":22,"9500e32e47f5c1f2f2fc57a6014d92e6":22,"9a3bcfc1b0bacf60542865403ea81002":22,"boolean":10,"case":[10,19,22,25,28],"class":[7,9,12],"default":[1,3,4,10,19,24,25,27],"export":[10,19,24],"float":10,"function":[0,4,5,9,10,12,19,21,23,25,26],"import":25,"long":[19,25],"new":[12,23],"null":22,"return":[1,6,9,10,12,28],"short":22,"true":[1,4,6,10,19,21,22],"try":[20,28],"var":24,"while":[19,21],AWS:21,Adding:23,DMs:[1,6],For:[4,19,21,22,26,27],IDs:19,IMs:[1,6],Not:1,PRs:20,SQS:[21,23,25],The:[0,1,6,9,10,12,19,21,24,25,26,27,28],There:19,These:25,Use:23,Using:24,__main__:21,_get_requests_sess:28,a1111aaaa:19,a1234abcd:19,a4321dcba:19,a6666zzzz:19,a6789wxyz:19,a87654321:[19,21,22],a9876zyxw:19,a_function_in_the_modul:19,abcd:21,abid:20,abl:[0,19],about:[9,19,21],abov:[19,22,27],accept:[0,4,19,20,21,28],access:[0,1,4,6,8,21,22,23,24],account:21,across:19,act:1,action:[0,1,4,6,9,19,22,27],action_t:[9,22],activ:24,add:[0,5,19,21,27],adding:19,addit:19,address:[1,6],adjust:19,admin:[0,21],after:[12,19],against:[1,4,6,19,21],agre:20,agreement:23,all:[1,4,12,19,20,22,25],allow:[0,1,4,19,25],allowed_path:[4,19,21],alon:19,along:22,also:[4,19,21,24,25,27,28],alwai:[0,27,28],america:22,amount:[19,25],ani:[0,10,19,21,22,25,27,28],announc:22,anoth:19,answer:19,anyth:[19,22],api:[0,3,4,9,21,22,23,25,27,28],app:[1,4,9,12,21,22,23,24,25],app_id:[19,25],appli:4,applic:[0,1,6],approach:21,apt:24,aren:24,arg:[22,27],argument:[1,6,7,10,12,24,27,28],as_us:[1,6],asctim:21,ask:[5,27],associ:[1,6,9,21,25],assum:19,assumpt:24,attach:[5,22,27],attempt:25,attende:22,attribut:[19,22],attribution_el:19,authent:4,authnz:[3,6,12,14,15,19,21,23],authnz_test:[12,14,15],author:[4,6,19,21],auto:[1,6,19,22,26],automat:[12,27],avail:[19,21,22],avatar:22,avatar_hash:22,avoid:21,aws_access_key_id:[8,19,21],aws_default_region:[19,21],aws_secret_access_kei:[8,19,21],aws_session_token:8,b456123:[1,6],b87654321:22,back:[5,19,21,22,25,27,28],backend:[21,28],bad:1,base:[7,9,12,19],bash:10,basi:4,basic:[0,1,4,5,6,21,23,27],bc1234567:[1,6],becaus:19,befor:[0,20,24],behalf:[1,19,27],being:25,below:22,between:[1,6,25],bigemoji_callback:5,bin:24,binari:21,bind:4,block:[10,21],bool_env:10,bootstrap:3,bot:[1,3,5,6,8,22,23,25,26,28],bot_id:[1,6,9,22],bot_messag:[1,6,22],bot_nam:[1,6,25],bot_receiv:25,bot_test:[12,14,15,17],both:[19,21,24],botinitializationerror:9,boto3:8,boto:21,botocor:19,broken_heart:[19,27],bug:20,build:[21,23],built:[4,19],button:[0,19,22],c12345:[1,6],c4vq6nunn:[1,6,22],c6kd0qx0q:22,cach:[0,9,19,21,25],call:[1,4,6,12,19,21,22,25,27,28],callback:[0,3,10,19,21,22,23,25,26],callback_id:[9,19,22,25],can:[0,1,5,19,20,22,24,25,27,28],canned_respons:19,cannot:[10,19],caus:21,certain:[0,19],chain:19,chang:[10,20,23,28],channel:[0,1,5,6,9,19,21,22,25,27],channel_channel_callback:5,channel_id:[9,22],channel_nam:[1,6],channel_response_callback:5,chat:[0,1,6,27],check:[4,5,6,19,21,24,27],checkbox:19,checkout:24,choos:24,cla:23,classmethod:9,click:[0,19,22],client:[3,8,9,12,28],client_kwarg:[5,28],client_typ:9,clone:23,cluster:4,code:[1,10,21,23,28],coerc:10,collabor:0,color:22,com:[0,1,6,19,21,22,24],combin:[19,24],combo:28,come:[1,6,19,22],command:[0,3,5,7,9,21,23,28],command_nam:25,command_text:9,common:[21,22,23],commun:[1,6,22],complain:21,compon:[0,3,5,9,10,23],component_typ:[9,25],compos:23,concurr:[19,21,25],condit:21,conduct:23,conf:[19,21,24],config:[4,8,19,21,24,28],config_fil:[19,24],configur:[0,1,4,6,7,21,23,24,25,28],conflict:21,congratulations_bot_callback:5,connect:[8,19,21],consid:25,consol:0,contain:[5,24,28],content:[1,23],context:4,continu:[19,21],contribut:23,contributor:23,control:[1,6,23],convent:28,convers:0,convert:25,copi:28,core:3,correctli:0,correl:19,correspond:10,cost:22,could:[1,6,19],count:25,counter:25,cpu:21,creat:[0,1,6,22,24,28],createsqsqueu:7,creator:[1,6,22],credenti:[0,21,23],credentials_slack_oauth_bot_token_:19,credentials_slack_oauth_bot_token_a1111aaaa:19,credentials_slack_oauth_bot_token_a87654321:[19,21],credentials_slack_oauth_token_:19,credentials_slack_oauth_token_a1111aaaa:19,credentials_slack_oauth_token_a87654321:[19,21],credentials_slack_verification_token_:19,credentials_slack_verification_token_a1111aaaa:19,credentials_slack_verification_token_a87654321:[19,21],criteria:19,critic:21,cross:25,current:[4,19,21,22,27],d1234567:[1,6],dashboard:[21,23,25],data:[0,9,19,21,22,23],daylight:22,dc1234567:[1,6],deactiv:24,debian:24,debug:[21,28],decid:0,decor:26,def:[12,19,28],defin:[4,19,25,28],delet:[1,6,22,25],delete_messag:3,deliv:19,deliveri:23,delivery_lat:25,deni:[4,19],depend:[0,19,21,28],deploi:24,deploybot:19,dequeu:[19,25],descript:[0,1,19,20,21,22,25,28],deseri:25,detail:[1,22],determin:25,dev:24,develop:[19,20,23],dialog:19,dict:[1,6,19,21,27],dictionari:[19,28],did:25,differ:19,direct:[1,6,9,19,22],directli:[19,21,24,27,28],disabl:[4,19],disallow:1,dispatch:3,displai:[0,19],display_nam:22,display_name_norm:22,distribut:25,do_someth:12,doc:[1,19,26],docbot:19,docker:23,document:[4,6,19,22,23,26,28],doesn:[0,1,6,19,21,22,27],don:[19,20,21,25,28],done:24,down:25,downstream:[4,22],drastic:25,dump:28,dure:12,each:[19,22,27],easi:19,easier:20,easiest:24,easili:20,east:[19,21],echo:[0,19],echo_callback:[5,19],echo_dialog_submission_callback:[5,19],echo_el:19,echo_submit:19,echobot:4,echobot_slack_act:4,edg:22,effort:19,either:19,element:19,email:[0,1,6,9,22,25],emoi:25,emoji:[0,5,22,25],empti:[10,19],enabl:[0,4],end:[19,25],endpoint:[4,6,19,21,23,27],endpoint_url:8,enforc:4,enforce_check:[4,6],enhanc:20,enqueu:[19,25],ensur:[0,4,21,25],enterprise_id:[9,22],enterprise_nam:[9,22],entir:0,env:[19,21,24],environ:[10,19,24],environn:19,envoi:[1,4,6,19],envoy_check:[3,19,23],envoy_checks_test:[12,14,15],envoy_internal_check:[4,19],envoy_permissions_check:[4,19],ephemer:[19,27,28],equal:19,err:24,error:[21,24,28],escap:0,etc:[19,21,22,24,27],evenbot:22,event:[0,3,4,6,9,19,21,23,26,27,28],event_t:25,event_trac:[3,9,28],event_typ:[6,25],eventbot:[22,28],eventbot_ev:22,eventu:21,everi:[0,19],everyon:20,everyth:22,exampl:[0,1,4,6,10,21,22,23,28],example_attachment_callback:5,example_topic_callback:5,except:[9,28],execut:4,exist:[12,28],experi:26,explicit:28,explicitli:[1,4,6],extern:[8,19,21],extra:[22,25,28],extract_channel:[9,25],extract_command:[9,25],extract_email:[9,25],extract_emoji:[9,25],extract_ment:[9,25],extract_speci:[9,25],extract_subteam:[9,25],extract_url:[9,25],extract_us:[9,25],fail:[21,25,28],failur:25,fake:21,fallback:[22,25],fals:[1,4,6,10,22],faq:19,fault:25,featur:[19,21],fetch:[9,19,25],few:25,field:[22,27,28],file:[0,23,24,25],filesystem:19,fill:27,find:[19,21,22,27],fine:21,first:19,first_nam:22,fixtur:12,flaki:19,flask:[12,26],flask_script:7,float_env:10,follow:[0,4,10,19,20,21,24],form:[19,24],format:[22,25,27,28],forward:21,found:[1,6],framework:[21,26],friendli:[21,22,25],from:[0,1,4,6,9,19,21,22,25,28],full:25,func:7,function_nam:28,g04939292775:22,g4939292775a:22,game:27,gcc:24,gener:[1,5,6,19,20,21,22,25,26],get:[0,1,3,6,8,9,10,12,22,24],get_bot_by_bot_id:9,get_bot_by_nam:9,get_bot_by_verification_token:9,get_bot_im:6,get_boto_cli:8,get_boto_sess:8,get_callback_id:10,get_channel:[1,6,9],get_channel_by_nam:[6,9],get_client:8,get_emoji:9,get_group:9,get_im:[1,6,9],get_im_channel_id:9,get_mpim:9,get_name_from_us:9,get_queue_url:8,get_redis_cli:8,get_statsd_cli:8,get_team:[1,4,6],get_team_by_id:9,get_team_by_nam:9,get_team_id_by_nam:6,get_us:[1,6,9],get_user_by_email:9,get_user_by_nam:9,get_user_v2:6,gevent:[19,23,24],git:24,github:[22,23,24],give:[5,22,27],given:[1,6,10],global:[9,12,28],got:28,govern:20,gravatar:22,group:[0,9,19,21,22,25],gunicorn:[19,24],handl:[6,19,22,25,27],handle_messag:[3,25],handler:[0,5,21,22,23,25,26,28],happen:19,has:[1,4,10,19,22,25,26,28],has_2fa:22,hasdfigasf97g9asfgsadgf9:22,have:[9,19,20,21,25,26,27],header:[1,4,6],healthcheck:6,hei:22,hello:[21,22],help:[5,19,20,21,22,24,25,26],help_callback:5,here:[0,1,5,6,19,21,22,24,27,28],herebot:19,high:25,higher:25,hint:0,histori:0,hold:21,hook:22,host:19,hostnam:[0,19],how:[1,19,22,25],http:[0,1,6,19,21,22,24,25,28],http_callback:[5,19,28],ident:19,ids:[19,25],ignor:[19,25],imag:23,image_192:22,image_24:22,image_32:22,image_48:22,image_512:22,image_72:22,immedi:19,implement:7,ims:[1,6,25],in_channel:[19,28],includ:[22,24,25,27],incom:21,incompat:21,increas:[19,25],indent:28,indic:[1,6],info:[5,9,21,22,26],infom:25,inform:[0,1,6,19,21,25],init:24,inject:[22,24],insid:19,instal:[0,21,23],instanc:[0,19,27],instead:[10,19,28],instruct:[0,20,24],instrument:19,instrument_ev:6,int_env:10,integ:10,integr:12,interact:[0,3,4,5,10,21,23],interactib:0,interactive_compon:[3,8,22,23,25],interactive_component_callback:[3,19,23],interactive_component_handl:[9,19],interactive_component_test:[12,14,15,17],interactive_messag:22,interactivecompon:9,intern:[1,4,5,6,19],internal_onli:4,interpret:12,invis:19,invit:21,invok:22,is_admin:22,is_app_us:22,is_archiv:[1,6,22],is_bot:22,is_channel:[1,6,22],is_gener:[1,6,22],is_im:[1,6],is_memb:[1,6,22],is_mpim:[1,6,22],is_org_shar:[1,6,22],is_own:22,is_primary_own:22,is_priv:[1,6,22],is_restrict:22,is_shar:[1,6,22],is_ultra_restrict:22,is_user_delet:[1,6],isn:[0,9,19,21,27],isol:21,issu:[21,23,25],item:28,its:[1,6,9,10,19,20,21,22,25],itself:21,join:22,jpg:22,json:[1,6,19,25,28],just:[5,24,27,28],keep:0,kei:[19,27],keyword:[1,6,12,27,28],know:19,kwarg:[1,3,4,6,19,21,27,28],label:19,lane:22,larg:[21,25],last_nam:22,last_set:[1,6,22],latenc:23,leav:19,less:19,let:[19,26,27,28],levelnam:21,libffi:24,librari:[21,23],libssl:24,libxml2:24,libxmlsec1:24,licens:23,like:[0,1,6,19,21,22,25,26,27,28],limit:[0,19,25],link:[0,21,27],list:[0,1,4,6,19,27],littl:19,local:[19,21],localhost:19,locat:[5,19,24],log:[21,23,24],log_config_fil:[19,21],logfil:24,logger:28,logic:3,longer:21,look:[22,24,25,27,28],lookup:27,loop:[21,25],los_angel:22,lot:21,lower:19,lyft:[19,20,21,22,24,28],mai:[6,9,19,21],main:3,major:19,make:[19,20,22,23,26,27,28],manag:[1,22],manual:23,map:[19,27],markup:22,match:[0,4,5,9,19,21,25,28],match_ment:19,match_typ:[9,19,21,28],max_pool_connect:19,maximum:25,mean:0,mechan:28,member:[1,6,22],member_count:19,mention:[9,25],menu:0,messag:[0,1,3,5,6,8,21,23,25,26],message_callback:[3,19,21,23],message_handl:[9,19,21,28],message_t:22,message_test:[12,14,15,17],messageunsupportederror:9,metadata:[19,21,22],metadataproxi:21,method:[4,20,24],metric:[19,25],migrat:19,minim:[10,23],minimum:[0,19,21],miss:[21,22,25],mkdir:24,mocker:[16,18],modul:[19,21,23,28],more:[1,19,25,26,28],most:[0,27],mpim:[0,9,21,22,25],msg:28,multipl:19,must:[4,7,19],my_set:12,mybot:[1,6],myemail:[1,6],myteam:[1,6],name:[0,1,3,4,6,9,10,12,19,21,22,25,27,28],name_norm:[1,6,22],necessari:[0,19,24],necessarili:21,need:[0,1,6,19,20,21,22,24,25,27],network:21,network_callback:[3,19,23,28],newer:10,nginx:4,ngrok:21,no_message_respons:19,non:[1,6,10,19,24],none:[3,5,7,8,9,22,27,28],normal:[21,22,23,27],note:[0,19,21,27],notic:28,notifi:19,now:27,num_memb:[1,6,22],number:[19,21,25],nutcrack:19,oauth:[0,9,19,21],oauth_bot_token:9,oauth_token:9,object:[1,6,9,12],observ:[19,23],occur:[22,25,28],omnibot:[0,1,12,14,19,22,25,27,28],omnibot_pars:[1,6,25,27],omnibot_payload_typ:22,omniredi:[3,23],one:[4,19,21],onli:[0,4,5,9,19,20,21,22],onlin:0,openssl:24,oper:[1,19,21],option:[7,19],order:[4,19],origin:[12,19,22],original_messag:22,other:[1,10,19,25],otherwis:[0,19,21],our:20,out:[24,27],outag:25,output:[19,21],over:27,overrid:[12,19,24,27],overridebot:19,overwrit:19,own:[21,22,27],pacif:22,packag:23,paramet:[1,6],pars:[0,1,6,9,23,25,27],parse_kwarg:3,parsed_channel:[9,22],parsed_text:[9,22],parsed_us:[9,22],parser:[3,8,23,25],parser_test:[12,14,15,17],part:[0,19,28],partial:[19,22],particip:20,particular:[19,25,28],pass:[1,4,6,19,25,27,28],path:[4,19,21,28],payload:[9,22,27,28],peopl:19,per:[4,19,22,25],perform:[1,4,6],permiss:[0,4,21],phone:22,ping:27,pip3:24,pip:[21,23],piptools_requirements3:24,pkg:24,plain:27,plan:20,pleas:[0,1,5,19,20,24,27],pluggabl:19,png:22,point:[0,19,22],poll:[0,19,21,25],pong:27,pool:[3,19,21,23],pool_nam:3,popul:19,port:19,posit:28,possibl:[4,19,20,21,27],post:[1,4,6,25,27,28],postmessag:[1,6,27],pre_sqs_delivery_lat:25,pre_sqs_delivery_retry_lat:25,prefix:19,prerequisit:23,prevent:19,preview:22,previous_nam:[1,6,22],primari:[19,21,23,25],primarili:[19,25],primary_bot:[19,21],prioriti:[1,6],privat:[0,19,24,25,27],probabl:24,proceed:0,process:[3,19,21,23],process_ev:[3,25],process_interactive_compon:[3,25],process_slash_command:[3,25],processor:23,product:[19,24],profil:22,project:20,properti:9,provid:[0,1,6,12,19,21,22,27],proxi:[19,21,23,28],pull:[23,24],purgeredi:7,purpos:[1,6,19,22],put:0,pystatsd:19,python3:24,python:[19,23,28],question:19,queue:[19,21],queue_ev:6,queue_pool:3,queue_url:3,quicker:20,quickli:22,quickstart:23,rais:10,random:19,rate:19,rather:[19,21,24,27,28],reach:25,reaction:[0,19,27],read:[0,19],real:5,real_nam:22,real_name_norm:22,realli:24,receiv:[0,9,19,22,23,25],recommend:[0,19,21],redi:[21,23,25],redis_host:[19,21],redis_port:[19,21],reduc:19,refer:[21,22,28],refresh:[22,25],refus:21,regex:[5,19],region:[8,21],regist:22,registr:22,registri:24,rel:[19,21],relat:25,relev:[4,19],remain:19,rememb:27,remov:[22,28],repars:22,repeat:21,replac:[19,21,27],replace_channel:9,replace_email:9,replace_speci:9,replace_url:9,replace_us:9,repo:21,repond:5,repopul:19,repres:9,reproduc:20,reqhead:6,request:[0,1,4,6,19,21,23,28],request_kwarg:[5,19,28],requestexcept:28,requir:[0,4,19,20,21,23,27,28],requirements3:24,reset:12,reshead:6,resourc:1,respond:[5,19,21,27,28],respons:[1,5,6,19,25,27,28],response_typ:[19,27,28],response_url:[9,22,27],rest:21,restart:[0,21],retri:25,retriev:10,rich:19,right:27,rlane:22,roughli:19,rout:[0,3,4,19,21,23,26,27],rule:10,run:[7,19,23,25],ryan:22,sai:19,same:[0,10,19,25,28],sandbox:[19,28],sanit:22,save:0,scope:[0,3,12,19],script:[3,23],search:[1,6],second:19,section:[4,19,21],secur:[19,22],see:[1,4,6,9,19,21,22,25,26],seeder:19,select:0,send:[0,1,6,19,21,22,27,28],send_bot_im:6,send_im:[1,6],sender:5,sensit:22,sent:[0,5,9,19,21,22,25,27],server:19,servic:[0,1,3,4,6,12,14,15,19,20,21,23,25,28],session:8,set:[0,1,4,5,6,12,19,21,23,27,28],set_match:9,settings_test:[12,14],settingsoverrid:12,setup:[0,21],setup_log:23,ship:19,should:[0,7,20,21,24,25,28],show:[0,25,27],sidebar:0,sign:23,similarli:[10,19],simpl:26,simpli:28,sinc:21,singl:19,skype:22,slack:[1,3,4,6,8,10,12,14,15,17,21,22,23,25,28],slack_action_v2:6,slack_api:4,slack_ev:6,slack_interactive_compon:6,slack_slash_command:6,slackact:1,slackclient:9,slash:[0,3,5,9,23,28],slash_command:[0,3,4,8,19,21,22,23,25],slash_command_callback:[3,19,23,28],slash_command_handl:[9,19,28],slashcommand:9,slask:25,slow:[19,25],some:[19,21,22,24],some_v:10,someon:27,someth:19,sometim:19,sourc:24,spawn:25,special:[1,5,6,9,19,22,25,27],special_callback:19,specials_callback:[5,19],specials_handl:19,specif:[19,25],specifi:[1,6,10,19,28],spend:25,split:22,sqs:[3,19,21,23,25],sqs_batch_siz:19,sqs_max_pool_connect:19,sqs_queue_nam:[19,21],sqs_url:[19,21],sqs_visibility_timeout:19,sqs_wait_time_second:19,srv:24,stackoverflow:19,stackoverflow_thread_prompt:19,stackoverflow_thread_submit:19,standard:[21,22,27],start:[4,21,24],startup:21,stat:[3,23],state:22,statsd:23,statsd_host:19,statsd_port:19,statsd_prefix:19,statu:[1,6,28],status_cod:28,status_emoji:22,status_expir:22,status_text:22,status_text_canon:22,statuscod:6,store:[21,24],str:[1,6,28],str_env:10,string:[1,6,10,19],structur:25,style:[22,26],subclass:7,subcommand:19,submiss:[9,19,22],submit:[19,23],submit_label:19,submodul:[14,17,23],subpackag:23,subscript:[0,6,9,19,21,23],subset:0,subteam:[22,25],subtyp:[1,6,9,22,25],success:[1,6],sudo:24,support:[0,19,21,22,25,28],system:[19,24,25],t12345678:[19,21,22],t123456:[1,6],t12345967:22,t1234abcd:19,t4321dcba:19,tableflip:[5,22,28],tableflip_callback:[5,28],take:[7,19,25,27,28],talk:[19,27],target:19,team:[0,1,3,6,8,21,22,23,25,28],team_id:[1,6,9,22,25],team_nam:[1,6],team_test:[12,14,15,17],teaminitializationerror:9,tell:[19,27],temporarili:12,term:20,test123:[1,6,22],test:[1,5,6,19,22,23,28],test_allowed_path:16,test_callback:[5,19,21],test_enforce_check:16,test_envoy_internal_check:16,test_envoy_permissions_check:16,test_extract_us:18,test_handl:[15,21],test_interactive_block_compon:18,test_interactive_compon:18,test_messag:18,test_my_funct:12,test_not_supported_extract:18,test_primary_slack_bot:15,test_slack_bot_token:15,test_slack_team:15,test_team:18,test_venmo_handl:22,testteam:4,text:[1,5,6,9,19,21,22,27,28],than:[19,21,24,25,27,28],thei:[0,4,19,21],them:[20,24],thi:[0,1,4,5,6,7,9,10,12,19,20,21,22,25,27,28],thing:[1,6,21,25,27],those:[19,21,27],though:[10,19,27],thread:[19,21,25,27],thread_t:[9,27],three:19,through:[6,19,20,24,25,27],time:[19,22,25],timer:25,titl:[19,22],todo:28,togeth:19,token:[0,21,22],topic:[1,5,6,22],total:22,trace:[19,23],track:[20,25],treat:10,trigger_id:[9,22,25],turn:[19,22],two:[4,10,19],txt:24,type:[0,1,6,19,22,25,28],tz_label:22,tz_offset:22,u1234567:[1,6],u123abc:[1,6],u4wf56qgp:[1,6,22],u6hqq19ec:[1,6,22],u6j3ltksq:[1,6,22],u6j4egp44:[1,6,22],u6jdf1jbu:[1,6,22],u6jegtfdz:[1,6,22],u6jerpmj7:[1,6,22],u6jg691mj:[1,6,22],u6jgeq0j0:[1,6,22],u6savuk44:[1,6,22],u750c7b37:[1,6,22],u7dh0h802:[1,6,22],uabc123:[1,6],ubuntu:24,unabl:[1,6],unexpand_metadata:25,unextract_channel:[9,25],unextract_speci:[9,25],unextract_us:[9,25],unflipt:5,unfliptable_callback:5,unformat:[19,21],unfortun:0,unintention:0,unit:12,unless:[4,21,27],unlik:27,unlink:[1,6,22],unpars:[22,25],unregist:22,unsupport:25,until:21,updat:22,update_channel:9,update_emoji:9,update_group:9,update_im:9,update_mpim:9,update_us:9,update_venmo:22,upon:19,url:[0,9,21,22,23,25,28],usag:[0,12,23],use:[1,5,6,10,19,21,23,24,27],used:[0,1,4,5,19,21,22,25,27],useful:[19,25],user:[0,1,6,9,19,21,22,25,27],user_id:[1,6,9,22],usernam:[0,1,6,9,22],uses:19,using:[0,1,6,10,12,19,23,25,26,27,28],util:[3,23],uwsgi:19,valid:22,valu:[0,1,3,6,10,12,19,22],valueerror:10,var_nam:10,variabl:[3,10,19,24],variou:22,venmo:22,venv:24,veri:[21,25],verif:[0,21],verifi:0,verification_token:9,verify_bot:6,version:[21,22,27],via:[1,19,20,21,24,25,26],virtualenv3:24,virtualenv:23,visit:[0,20],wai:[19,21],wait_avail:3,want:[0,19,21,22,24,27,28],warn:19,wasn:25,watch:25,watch_channel:[3,25],watch_emoji:[3,25],watch_group:[3,25],watch_im:[3,25],watch_mpim:[3,25],watch_us:[3,25],watcher:[0,19,21,23,24],web:19,webhook:[6,19,21,23],webhook_1:21,webhook_work:[23,24],webhook_worker_concurr:19,webhookpool:25,well:[19,21,27],were:10,what:[19,21,22,27],whatev:[5,19,28],when:[12,19,20,22,24,25,27,28],where:19,whether:[0,1,6,25],which:[0,4,19,21,22,24,27,28],whichev:19,why:22,wide:[1,6,22],within:[1,21,28],without:[19,21,28],won:21,word:27,work:[0,19,21],worker:[19,21,23,24],workload:19,workspac:[0,1,4,21,25],world:22,would:[0,4,27],wouldn:19,wrapper:9,write:[0,19,23,24,26],wsgi:[19,23,24],xoxb:[19,21],xoxp:[19,21],yaml:[19,21,25],yet:0,yield:21,you:[0,1,6,19,21,22,24,25,26,27,28],your:[0,19,20,21,22,24,26,27,28],yourself:22},titles:["Adding new slack apps","API","manage module","omnibot package","omnibot.authnz package","omnibot.callbacks package","omnibot.routes package","omnibot.scripts package","omnibot.services package","omnibot.services.slack package","omnibot.utils package","setup module","tests package","tests.integration package","tests.unit package","tests.unit.omnibot package","tests.unit.omnibot.authnz package","tests.unit.omnibot.services package","tests.unit.omnibot.services.slack package","Configuration","Contributing","Quickstart and Development","Event parsing","Omnibot","Installation","Observability","Omnibot receiver libraries","Slack proxying","Writing new callback functions"],titleterms:{"function":28,"new":[0,21,28],Adding:0,SQS:19,Use:19,access:19,agreement:20,api:[1,6,19],app:[0,3,19],authnz:[4,16],authnz_test:16,basic:19,bot:[0,9,19,21],bot_test:18,build:24,callback:[5,28],chang:21,cla:20,clone:24,code:20,command:[19,22,25,27],common:19,compon:[19,22,25,27],compos:21,conduct:20,configur:19,conftest:12,content:[3,4,5,6,7,8,9,10,12,13,14,15,16,17,18],contribut:20,contributor:20,control:19,credenti:19,dashboard:19,data:25,deliveri:25,develop:21,docker:[21,24],document:1,envoy_check:4,envoy_checks_test:16,event:[22,25],exampl:19,file:[19,20],gevent:25,github:20,handler:[19,27],imag:24,instal:24,integr:13,interact:[19,22,25,27],interactive_compon:9,interactive_component_callback:5,interactive_component_test:18,issu:20,latenc:25,librari:26,licens:20,log:[19,25],make:[21,24],manag:2,manual:24,messag:[9,19,22,27],message_callback:5,message_test:18,minim:19,modul:[2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],network_callback:5,normal:0,observ:25,omnibot:[3,4,5,6,7,8,9,10,15,16,17,18,21,23,24,26],omniredi:[7,8],packag:[3,4,5,6,7,8,9,10,12,13,14,15,16,17,18],pars:22,parser:9,parser_test:18,pip:24,pool:25,prerequisit:21,primari:0,process:25,processor:3,proxi:27,pull:20,python:26,quickstart:[21,24],receiv:26,redi:19,request:20,requir:24,rout:[1,6],run:24,script:7,servic:[8,9,17,18],set:[3,10],settings_test:15,setup:11,setup_log:3,sign:20,slack:[0,9,18,19,27],slash:[19,22,25,27],slash_command:9,slash_command_callback:5,sqs:8,stat:[8,25],statsd:19,submit:20,submodul:[3,4,5,6,7,8,9,10,12,15,16,18],subpackag:[3,8,12,14,15,17],subscript:[22,25],team:[9,19],team_test:18,test:[12,13,14,15,16,17,18,21,24],trace:25,unit:[14,15,16,17,18],url:19,use:0,using:21,util:[7,10],virtualenv:24,watcher:[3,25],webhook:25,webhook_work:3,worker:25,write:28,wsgi:3}})