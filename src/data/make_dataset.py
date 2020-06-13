# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import os
import sqlite3
import pandas as pd
import json
from src.data.process_quizzes import process_quizzes

@click.command()
@click.argument('input_filepath', type=click.Path(exists=True))
@click.argument('output_filepath', type=click.Path())
def main(input_filepath, output_filepath):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')

    #logger.info('processing quizzes into database')
    #process_quizzes(input_filepath, output_filepath)

    logger.info('Loading consenting')
    consenting = pd.read_csv(os.path.join(input_filepath, 'consenting.txt'), squeeze=True)

    logger.info('Collecting demographics')
    demographics = pd.read_csv(os.path.join(input_filepath, 'demographics.csv'))

    logger.info('Getting pokemon')
    pokemon = pd.read_csv(os.path.join(input_filepath, 'pokemon.txt'))

    only_consenting = demographics[demographics.Email.isin(consenting)]

    blockpy = pd.read_sql("""SELECT SubjectID, `X-Email` as Email
                            FROM LinkSubject""",
                           sqlite3.connect(os.path.join(output_filepath, "progsnap2_7.db")))
    only_consenting = only_consenting.merge(blockpy, on='Email')
    only_consenting.insert(1, 'pokemon', pokemon)
    #only_consenting['pokemon'] = pokemon

    logger.info('Remove identifying data')
    del only_consenting['Email']
    del only_consenting['ID']
    del only_consenting['CanvasID']

    only_consenting.to_csv(os.path.join(output_filepath, "subjects.csv"), index=False)

    '''
    # Deprecated in favor of just manually creating
    with open(os.path.join(input_filepath, 'lock_dates.json')) as lock_dates_file:
        lock_dates = json.load(lock_dates_file)
    lock_dates = lock_dates['data']['course']['assignmentsConnection']['nodes']
    lock_dates = [{'AssignmentId': ld['name'], 'lock': ld['lockAt']} for ld in lock_dates]
    pd.DataFrame(lock_dates).to_csv(os.path.join(output_filepath, 'lock_dates.csv'), index=False)
    '''


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
