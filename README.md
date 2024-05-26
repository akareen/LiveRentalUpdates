# Live Rental Updates

Welcome to the Live Rental Updates project! This project aims to provide real-time updates on new Australian rental property listings in specified postcodes that match a given price point. The project consists of web scraping, data processing, and a front-end interface. Over the coming weeks, the project will be extended to include database integration and automated email notifications.

COMING SOON™️ - Website where you can add your email address and preferences to receive live updates on new rental listings that match your criteria.

## Project Structure

1. **Web Scraping**: The core of this project involves scraping rental listings from real estate websites. The scraping scripts are written in Python and utilize the BeautifulSoup library to parse HTML content.
2. **Data Processing**: After scraping the listings, the data is processed to extract relevant information such as price, location, and property features.
3. **Front-End Interface**: A demo front-end interface allows users to input their email addresses, maximum price points, and postcodes of interest. This interface will eventually connect to the backend to send email updates.

## Features

- **Scraping**: Extracts rental listings from various real estate websites.
- **Postcode Validation**: Ensures that only valid Australian postcodes are processed.
- **Price Conversion**: Converts various price formats to a weekly price for uniformity.
- **Data Storage**: Stores scraped data in a CSV file.
- **Front-End Interface**: Allows users to input their preferences for rental updates.

## Future Development

- **Database Integration**: Connect the scraping results to a database to store listings and user preferences.
- **Email Notifications**: Implement a system to send email notifications every 5 minutes when new properties matching the user's criteria are found.
- **Enhanced Front-End**: Improve the front-end to provide a more interactive user experience.

## Usage

### Prerequisites

- Python 3.6+
- Required Python libraries: `requests`, `beautifulsoup4`, `pandas`, `concurrent.futures`, `flask`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/akareen/LiveRentalUpdates.git
   cd LiveRentalUpdates
   ```

2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Scraper

1. Run the main scraping script:
   ```bash
   python main.py
   ```
   This will scrape listings from the specified websites and store the results in `output.csv`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or suggestions, please contact me at me@akareen.com

---

Thank you for checking out the Live Rental Updates project. Stay tuned for more updates as we continue to enhance the functionality and features of this project!