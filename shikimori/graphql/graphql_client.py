import httpx
import logging
import time
import threading

from requests import Response
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport, ExecutionResult

from typing import Any, Dict


class GraphQLAuthError(Exception):
    """
    An exception raised for errors related to authentication token methods.
    """


class GraphQLClient:
    """
    A client for interacting with a GraphQL API, supporting authentication and query execution.

    Attributes
    ----------
    url : str
        The base URL of the GraphQL API.
    client : Client or None
        The initialized GraphQL client, or None if not initialized.
    """

    def __init__(self, logger: logging.Logger, url: str) -> None:
        """
        Initialize the GraphQLClient.

        Parameters
        ----------
        url : str
            The base URL of the GraphQL API.
        """
        self.logger = logger
        self.url = url

        self.client: Client | None = None

        # general client constants
        self._auth_url: str = "https://shikimori.one/oauth/token"
        self._auth_headers: Dict[str, str] = {
            "User-Agent": "Api Test",
        }
        self._token_auth_params: Dict[str, str] = {
            "client_id": "bce7ad35b631293ff006be882496b29171792c8839b5094115268da7a97ca34c",
            "client_secret": "811459eada36b14ff0cf0cc353f8162e72a7d6e6c7930b647a5c587d1beffe68",
        }

    def get_access_token(self, auth_code: str) -> Response:
        """
        Obtain an access token using an authorization code. See in more details shiki OAuth2 Guide:
        https://shikimori.one/oauth?oauth_application_id=15

        Parameters
        ----------
        auth_code : str
            The authorization code obtained from the OAuth2 flow.

        Returns
        -------
        Response
            The HTTP response containing the authentication access token.

        Raises
        ------
        GraphQLAuthError
            If the authorization fails or a request error occurs.
        """
        with httpx.Client() as client:
            try:
                response = client.post(
                    url=self._auth_url,
                    data=self._get_auth_params(auth_code),
                    headers=self._auth_headers,
                )

                if response.status_code != 200:
                    raise GraphQLAuthError(f"Authorization failed: {response.text}")

                return response

            except httpx.RequestError as e:
                raise GraphQLAuthError(
                    f"An error occurred while requesting auth code: {e}"
                )

    def refresh_access_token(self, refresh_token: str) -> Response:
        """
        Refresh an expired authentication token. See in more details shiki OAuth2 Guide:
        https://shikimori.one/oauth?oauth_application_id=15

        Parameters
        ----------
        refresh_token : str
            The refresh token used to obtain a new authentication token.

        Returns
        -------
        Response
            The HTTP response containing the refreshed authentication token.

        Raises
        ------
        GraphQLAuthError
            If refreshing the token fails or a request error occurs.
        """
        with httpx.Client() as client:
            try:
                response = client.post(
                    url=self._auth_url,
                    data=self._get_refresh_params(refresh_token),
                    headers=self._auth_headers,
                )

                if response.status_code != 200:
                    raise GraphQLAuthError(f"Failed to refresh token: {response.text}")

                return response

            except httpx.RequestError as e:
                raise GraphQLAuthError(
                    f"An error occurred while requesting refresh token: {e}"
                )

    def init(self, access_token: str) -> None:
        """
        Initialize the GraphQL client with an authentication token.

        Parameters
        ----------
        access_token : str
            The authentication access token to authorize the client.
        """

        transport = self._get_transport(access_token)
        self.client = Client(transport=transport, fetch_schema_from_transport=True)

    def execute(
            self,
            query: str,
            variables: dict[str, Any] | None = None,
            max_pages: int = 10
    ) -> list[Any] | ExecutionResult:
        """
        Execute a GraphQL query, paginating through the results if necessary.

        Parameters
        ----------
        query : str
            The GraphQL query string.
        variables : dict[str, Any], optional
            A dictionary of variables for the query, by default None.
        max_pages : int
            The maximum number of pages to fetch (default is 10).

        Returns
        -------
        dict[str, Any] or ExecutionResult
            The result of the query execution.
        """
        if variables is None:
            variables = dict()

        all_results = []
        stop_event = threading.Event()
        log_thread = threading.Thread(target=self._log_parsing(stop_event), daemon=True)
        log_thread.start()

        start_time = time.time()

        for page in range(1, max_pages + 1):
            variables['page'] = page

            try:
                query_obj = gql(query)
                result = self.client.execute(query_obj, variable_values=variables)

                if result:
                    for key, value in result.items():
                        if isinstance(value, list):
                            all_results.extend(value)
                        else:
                            self.logger.warning(f"Unexpected structure for key '{key}', skipping.")
                else:
                    self.logger.warning(f"No data received for page {page}.")

                if not result or not any(isinstance(value, list) for value in result.values()):
                    self.logger.info(f"No more data found, stopping at page {page}.")
                    break

                self.logger.info(f"Page {page} fetched successfully.")

            except Exception as e:
                self.logger.error(f"Error while fetching page {page}: {e}")
                break

        self.logger.info(f"Execution completed in {time.time() - start_time:.2f} seconds")
        return all_results

    def _get_auth_params(self, auth_code: str) -> Dict[str, str]:
        auth_params: Dict[str, str] = self._token_auth_params

        auth_params["grant_type"] = "authorization_code"
        auth_params["code"] = auth_code
        auth_params["redirect_uri"] = "urn:ietf:wg:oauth:2.0:oob"

        return auth_params

    def _get_refresh_params(self, refresh_token: str) -> Dict[str, str]:
        refresh_params: Dict[str, str] = self._token_auth_params

        refresh_params["grant_type"] = "refresh_token"
        refresh_params["refresh_token"] = refresh_token

        return refresh_params

    def _get_transport(self, token: str) -> AIOHTTPTransport:
        headers = self._auth_headers
        headers["Authorization"] = f"Bearer {token}"

        return AIOHTTPTransport(url=self.url, headers=headers)

    def _log_parsing(self, stop_event: threading.Event):
        while stop_event.is_set():
            self.logger.info("Execution is in progress...")
            time.sleep(1)

