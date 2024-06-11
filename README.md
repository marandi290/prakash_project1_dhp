# Text Analysis Flask App

This is a Flask web application for analyzing news articles. It allows users to input a URL of a news article, extracts the text content, performs various analyses such as counting sentences, words, and identifying parts of speech (POS), and then displays the analysis results.

## Features

- **User Authentication**: Users can log in using their GitHub accounts.
- **Admin Verification**: Certain functionalities are restricted to admin users. Admins can access additional features after verification.
- **Text Analysis**: Extracts text content from news articles, analyzes them for various metrics, and stores the results in a PostgreSQL database.
- **Data Viewing**: Users can view the analyzed data, including titles, content, sentence count, word count, stopword count, and POS tags.
- **Admin Panel**: Admins can view URLs of all analyzed news articles.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/<username>/<repository_name>.git
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up environment variables:

    - `SECRET_KEY`: A secret key for the Flask app.
    - `GITHUB_CLIENT_ID`: Client ID for GitHub OAuth.
    - `GITHUB_CLIENT_SECRET`: Client Secret for GitHub OAuth.

4. Set up the PostgreSQL database:

    - Create a database named `text_analyze`.
    - Create a table named `news_table` with columns: `Title`, `News`, `Sentence_no`, `Words_no`, `Stopwords_no`, `Postages`, `url`.

5. Run the application:

    ```bash
    python app.py
    ```

## Usage

1. Visit the homepage and input the URL of a news article.
2. Click on the "Analyze" button to analyze the article.
3. View the analysis results on the details page.
4. Admins can access additional functionalities by verifying their admin status.

## Contributing

Contributions are welcome! Feel free to fork the repository, make changes, and submit pull requests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
