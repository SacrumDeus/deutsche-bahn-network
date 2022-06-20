# system imports
from datetime import datetime
import json
import logging
import requests
import urllib.parse

# external imports
import pandas as pd
from pymongo import MongoClient
import tqdm


class dataDB:
    """    
    This class can be used to retrieve data from various APIs from "Deutsche Bahn". These APIs will be used:

    * Fahrplan - v1

    Please note, that a mandatory API key is required. This key can be obtained from "Deutsche Bahn" (https://developer.deutschebahn.com/store/apis/list)
    """

    # class constants
    API_DEPARTURE = 'https://api.deutschebahn.com/fahrplan-plus/v1/departureBoard/{id}?date={date}'
    API_JOURNEY = 'https://api.deutschebahn.com/fahrplan-plus/v1/journeyDetails/{id}'
    MONGO = 'mongodb://localhost:27017/'

    def __init__(self) -> None:
        """
        Constructor for class 'dataDB'.

        Arguments:
        ----------
            * token (str): API token, which can be obtained from 'Deutsche Bahn'

        Returning:
        ----------
            * None

        ----
        Constructor for class 'dataDB'. This method will establish a connection to a database (MongoDB), which will store the data for further processing.

        Furthermore, many variables will be initiated, which is required for processing.
        """

        # init various variables
        self.apiToken = None
        self.stations = None
        self.trainList = list()

        # init mongodb connection
        self.mongoClient = MongoClient(self.MONGO)
        self.mongoDatabase = self.mongoClient["deutscheBahn"]

        # prepare mongodb - collections (collections were created manually)
        self.mongoCol_station = self.mongoDatabase["station"]
        self.mongoCol_train = self.mongoDatabase["train"]
        self.mongoCol_stops = self.mongoDatabase["stops"]

        # init collections to prevent duplicates
        if self.mongoCol_station.count_documents({}) > 0:
            self.mongoCol_station.delete_many({})
        if self.mongoCol_train.count_documents({}) > 0:
            self.mongoCol_train.delete_many({})
        if self.mongoCol_stops.count_documents({}) > 0:
            self.mongoCol_stops.delete_many({})

        # init logging
        logging.basicConfig(filename='error-log.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s', filemode='w')
        self.logger = logging.getLogger(__name__)

    def setApiToken(self, token: str) -> None:
        """
        This method stores the API token in the object.

        Arguments:
        ----------
            * token (str): API token, which can be obtained from 'Deutsche Bahn'

        Returning:
        ----------
            * None

        ----
        This method stores the API token in the object. The API token can be obtained from `Deutsche Bahn` and is mandatory for retrieving the data.
        """
        self.apiToken = token

    def setTrainStations(self, link: str, delimiter: str = ';') -> None:
        """
        There is a list of all train stations avaibable, which is stored in the object.

        Arguments:
        ----------
            * link (str): URL to train station list
            * *delimiter (str): Delimiter of CSV file. Default: ';'

        Returning:
        ----------
            * None

        ----
        There is a list of all train stations available, which stores the data as CSV-file. Since we are only obtaining long 
        distance connections (like IR, IC, ICE, ...), we will filter the data for `Verkehr == 'FV'`. The data are stored in the object
        """

        # get data from link
        stations = pd.read_csv(link, sep=delimiter)
        
        # store data in mongoDb - station
        self.mongoCol_station.insert_many(self.stations.to_dict('records'))

        # filter dataframe
        self.stations = stations[stations['Verkehr'] == 'FV']

        # reset index
        self.stations.reset_index(drop=True, inplace=True)

    def startDataExtraction(self) -> None:
        """
        This function is the entry point to extract the data from 'Deutsche Bahn'.

        Arguments:
        ----------
            * None

        Returning:
        ----------
            * None

        ----
        This function extracts all data from 'Deutsche Bahn' for the given train stations. The data will be stored in MongoDb

        Please note, that this method spawns multiple processes and uses the multiprocessing technology. This function wont work properly in Jupyter notebooks.
        """

        # variables
        trainStationData = list()

        # we need to check API token
        if self.apiToken is None:
            raise AttributeError(
                'Missing variable `apiToken`. Please run method `setApiToken()`.')

        # we need to check train stations
        if self.stations is None:
            raise AttributeError(
                'Missing variable `stations`. Please run method `setTrainStations()`.')

        # progress bars
        progressTSBar = tqdm.tqdm(total=len(self.stations["EVA_NR"].values), desc="Train stations", position=0)
        progressTsMsg = tqdm.tqdm(total=len(self.stations["EVA_NR"].values), bar_format='{desc}', position=1)

        # extract the train station data (EVA numbers)
        for ts in self.stations["EVA_NR"].values:

            # update progress msg
            progressTsMsg.set_description_str(f'=> Current train station: {ts}')

            # get data
            trainStationData.extend(self.getTrainStationData(str(ts)))

            # update progress bar
            progressTSBar.update()

        # extract the detail data for each train
        for train in tqdm.tqdm(trainStationData, desc="Train details", position=0):
            self.getTrainJourneyDetail(train["detailsId"], train["name"])

    def getRequest(self, link: str) -> json:
        """
        This method returns the data from a given link as JSON object.

        Arguments:
        ----------
            * link (str): Link to data

        Returning:
        ----------
            * json: json object of returned data

        Description:
        ------------
            This method returns the data from a given link as JSON object.
        """

        # create header dict
        headers = {}

        # set header data
        headers["Accept"] = "application/json"
        headers["Authorization"] = f'Bearer {self.apiToken}'

        # get data
        response = requests.get(link, headers=headers)

        # validate response
        if response.status_code != 200:
            raise response.raise_for_status()

        # return json
        return response.json()

    def getTrainStationData(self, station: str) -> list:
        """
        This method is used to retrieve the station data from 'Deutsche Bahn' for a single day.

        Arguments:
        ----------
            * station (str): EVA Code for train station

        Returning:
        ----------
            * list

        ----
        This method is used to retrieve the station data from 'Deutsche Bahn' for a single day. 
        Returned is a list, which contains the train station data. Duplicates will be filtered.
        """

        # variables
        exitCondition = False
        currentDate = datetime(2022, 7, 1, 00, 00, 00)
        returnList = list()

        # start/end date
        startDate = datetime(2022, 7, 1, 00, 00, 00)
        endDate = datetime(2022, 7, 1, 23, 59, 59)

        # retrieve data for complete day
        while exitCondition == False:

            # create link
            link = self.API_DEPARTURE.format(id=station,
                                             date=currentDate.isoformat())

            try:
                # get data
                departureData = self.getRequest(link)

                # check length of departureData
                if len(departureData) == 0:
                    exitCondition = True
                elif len(departureData) < 20:
                    exitCondition = True
                else:
                    exitCondition = False

                # process each train
                for train in departureData:

                    # get time of train
                    trainDate = datetime.fromisoformat(train["dateTime"])

                    # validate date
                    if startDate < trainDate < endDate:

                        # set current date
                        currentDate = trainDate

                        # check for duplicates
                        if train["name"] not in self.trainList:

                            # append to returnList + self.trainList
                            returnList.append(train)
                            self.trainList.append(train["name"])

                            # insert in MongoDb
                            self.mongoCol_train.insert_one(train)

                        else:
                            continue

                    else:

                        # set exitCondition
                        exitCondition = True

                        # leave for loop
                        break

            except Exception as err:

                # log error
                self.logger.exception(err)

                # set exit condition
                exitCondition = True

        # return returnList
        return returnList

    def getTrainJourneyDetail(self, detailsId: str, trainName: str) -> None:
        """

        Arguments:
        ----------
            * detailsId (str): detailsId from train data
            * trainName (str): name of the train

        Returning:
        ----------
            * None

        ----
        This methods gets the detail data for each train from 'Deutsche Bahn'. This is achieved by passing detailsId, which can be obtained from the results from `departureBoard`.

        The results will be stored in MongoDb.
        """

        try:

            # create link
            link = self.API_JOURNEY.format(id=urllib.parse.quote(detailsId))

            # create dict + get data
            trainData = dict()
            trainData["name"] = trainName
            trainData["stop"] = self.getRequest(link)

            # insert into MongoDb
            self.mongoCol_stops.insert_one(trainData)

        except Exception as err:
            
            # log error
            self.logger.exception(err)

            # return
            return
