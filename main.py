from ph_dailyweather_scraper import scrape_DailyWeather
from ph_damlevel_scraper import scrape_DamLevel

if __name__ == "__main__":
    print("Now scraping for yesterday's PH weather data...")
    scrape_DailyWeather()
    print("Now scraping for today's PH dam water level data")
    scrape_DamLevel()