#collective simple file to call three classes as tedious to run each one seperately
import SteamScraper as steam
import SteamChartsScraper as steamCharts
import HLTBScraper as hltb

#get data from steam
manager =steam.SteamScraper()
manager.update_catalog(target_count=10000)
#then get the corresponding steamcharts data
scraper = steamCharts.SteamChartsScraper()
scraper.update_catalog()
#then get the relevant data from how long to beat
scraper = hltb.HLTBScraper()
scraper.update_catalog()