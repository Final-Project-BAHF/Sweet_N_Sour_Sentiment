from bs4 import BeautifulSoup as bs
import re

def get_article_list(session, ticker):
    """Return a list of dictionaries detailing the articles found for the requested ticker. 
        Source: SeekingAlpha.com.

        Argument: session - an HTTP session to use for scraping SeekingAlpha.com
        Argument: ticker - the stock ticker of the company to search for

        Returns:
            List of dictionaries describing each Earnings Call found in following format:
              {
                'ticker': stock_ticker,
                'title': article_title,
                'url': article_url
              }
       """

    base_url = 'https://seekingalpha.com'
    articles_url = base_url + '/symbol/' + ticker + '/earnings/transcripts'

    headers = {
        'authority': 'seekingalpha.com',
        'method': 'GET',
        'path': '/symbol/ORCL/earnings/transcripts',
        'scheme': 'https',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        'pragma': 'no-cache',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'cache-control': 'no-cache',
        'referer': articles_url
    }

    # Retrieve page with the requests module
    response = session.get(articles_url, headers=headers)

    #DEBUG
    #print(response)
    #print(response.text)
    #

    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(response.text, 'lxml')

    # collect news articles
    articles = soup.find_all('div', class_="symbol_article")

    # build list of article titles and urls, but only for call transcripts (last 3 words of title are "Earnings Call Transcript")
    articles_details = []
    for article in articles:
        a_tag = article.find('a')
        article_title = a_tag.text
        article_url = base_url + a_tag.get('href') + '?part=single'
        if (article_title[-24:] == 'Earnings Call Transcript'):
            articles_details.append({
                'ticker': ticker,
                'title': article_title,
                'url': article_url
            })

    return articles_details

def get_call_content(session, call_url, ticker):
    """Return a dictionary detailing the requested transcript 
        Source: SeekingAlpha.com.

        Argument: session - an HTTP session to use for scraping SeekingAlpha.com
        Argument: call_url - the url of the Earnings Call Transcript to parse
        Argument: ticker - stock ticker of company for requested call

        Returns:
            Dictionary containing the contents of the Earnings Call in the following format:
                {
                    'ticker': ticker symbol of company,
                    'eps_info': text describing the EPS performance compared to analyst estimates,
                    'revenue_info': text describing the Revenue performance compared to analyst estimates,
                    'call_title': title of earnings call -- contains date and time of the call,
                    'company_participants': [{
                            'name': Participant Name,
                            'company': Participant Employer,
                            'affiliation': 'host'  <i>#indicates this participant is a member of the hosting company for the call</i>
                    }
                    ...
                    ],
                    'call_participants': [{
                            'name': Participant Name,
                            'company': Participant Employer,
                            'affiliation': 'guest'  <i>#indicates this participant is a guest attendee of the call</i>
                    }
                    ...
                    ],
                    'paragraphs': [{
                            'speaker': name of speaker,
                            'content': paragraph of text from transcription for this given speaker,
                            'call_section': specifies the section of the call in which this content was spoken ('presentation', 'operator_instruction', 'question', 'answer')
                    }
                    ...
                    ]
                }
       """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
        'pragma': 'no-cache',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'cache-control': 'no-cache',
        'referer': call_url
    }

    # Retrieve page with the requests module
    response = session.get(call_url, headers=headers)

    # Create BeautifulSoup object; parse with 'lxml'
    soup = bs(response.text, 'lxml')

    # collect paragraphs
    paragraphs = soup.find_all('p')

    # prep dictionary for transcript
    call_dict = {
        'ticker': ticker,
        'eps_info': '',
        'revenue_info': '',
        'call_title': '',
        'company_participants': [],
        'call_participants': [],
        'paragraphs': []
    }

    # setup expected sequence of paragraphs in transcript
    p_sequence = ['title','participant_hdr1','company_participants','particpant_hdr2','call_participants',
                'speaker_name1','text1','qa_hdr','speaker_name2','text2']

    # keep track of progress through sequence
    sequence_index = 0

    # setup dict for speaker/paragraph pairs
    current_p = {
        'speaker': '',
        'content': '',
        'call_section': ''
    }

    for p in paragraphs:
        
        if (p_sequence[sequence_index] == 'title'):
            
            # grab call title
            call_dict['call_title'] = p.text
            
            # advance our sequence tracker
            sequence_index += 1
            
        elif (p_sequence[sequence_index] == 'participant_hdr1'):
            
            # check that we found the header
            if (p.text == 'Company Participants'):
                
                # advance our sequence tracker
                sequence_index += 1
                
        elif (p_sequence[sequence_index] == 'company_participants'):
            
            # check that we did not find the next header yet
            if (p.text != 'Conference Call Participants'):
                
                # we found a name, parse name and title
                #print(p.text) # DEBUG
                name, title = re.split('\s[–-]\s',p.text)
                
                # populate participant name and title into call dictionary
                call_dict['company_participants'].append({
                    'name': name,
                    'title': title,
                    'affiliation': 'host'
                })
                
                # don't advance sequence tracker since we may have more names
            
            else:
                
                # found next participant header, skip ahead by 2
                sequence_index += 2
            
        elif (p_sequence[sequence_index] == 'participant_hdr2'):
            # should never get here, do nothing
            continue
            
        elif (p_sequence[sequence_index] == 'call_participants'):
            
            # check that we did not find first speaker yet

            if (p.contents[0].name != 'strong'):

                # we found a name, parse name and company
                #print(p.text) # DEBUG
                name, company = re.split('\s[–-]\s',p.text)
                
                # populate participant name and company into call dictionary
                call_dict['call_participants'].append({
                    'name': name,
                    'company': company,
                    'affiliation': 'guest'
                })
                
                # don't advance sequence tracker since we may have more names
            
            else:

                # found first speaker reference, capture name, section, and increment sequence tracker by 2
                current_p['speaker'] = p.text
                if (p.text == 'Operator'):
                    current_p['call_section'] = 'operator_instruction'
                else:
                    current_p['call_section'] = 'presentation'
                sequence_index += 2
            
        elif (p_sequence[sequence_index] == 'speaker_name1'):
            # should never get here
            continue
        elif (p_sequence[sequence_index] == 'text1'):
            
            # make sure we have not found next section indicated by <strong>
            if (p.contents[0].name != 'strong'):
                
                # append content to current_p
                current_p['content'] += ' ' + p.text
                
            else:
                
                # we found another section, check for Q/A Header
                if (p.text == 'Question-and-Answer Session'):
                    
                    # add current_p to call_dict
                    call_dict['paragraphs'].append(current_p)
                    
                    # reset current_p
                    current_p = {
                        'speaker': '',
                        'content': '',
                        'call_section': ''
                    }
                    
                    # we are entering Q/A, force tracker to index 8 - speaker2
                    sequence_index = 8
                    
                else:
                    
                    # new speaker, not Q/A yet
                    
                    # add currrent_p to call_dict
                    call_dict['paragraphs'].append(current_p)
                    
                    # reset current_p
                    current_p = {
                        'speaker': p.text,
                        'content': '',
                        'call_section': 'presentation'
                    }
                    
                    # no need to advance tracker as we were on text1 but found another speaker1, next section 
                    # should again be text1
                            
        elif (p_sequence[sequence_index] == 'qa_hdr'):
            # should never get here
            continue
            
        elif (p_sequence[sequence_index] == 'speaker_name2'):
            
            # first speaker in Q/A section
            current_p['speaker'] = p.text
    
            # set call section appropriately...
            span = p.find('span')
            span_class = ''
            if (span):
                span_class = span['class'][0]

            # check if operator
            if (p.text == 'Operator'):   
                current_p['call_section'] = 'operator_instruction'
            # check if question
            elif (span_class == 'question'):
                current_p['call_section'] = 'question'
            # check if answer
            elif (span_class == 'answer'):
                current_p['call_section'] = 'answer'
            # default to presentation, in case of closing remarks for example
            else:
                current_p['call_section'] = 'presentation'     
                
            # advance sequence tracker
            sequence_index += 1
            
        elif (p_sequence[sequence_index] == 'text2'):

            # make sure we have not found next speaker indicated by <strong>
            if (p.contents[0].name != 'strong'):
                
                # append content to current_p
                current_p['content'] += ' ' + p.text
                
            else:
                
                # we found another speaker, add current_p to call_dict and reset
                call_dict['paragraphs'].append(current_p)
                
                # reset current_p
                current_p = {
                    'speaker': p.text,
                    'content': '',
                    'call_section': ''
                }
                
                # set call section appropriately...
                span = p.find('span')
                span_class = ''
                if (span):
                    span_class = span['class'][0]

                # check if operator
                if (p.text == 'Operator'):   
                    current_p['call_section'] = 'operator_instruction'
                # check if question
                elif (span_class == 'question'):
                    current_p['call_section'] = 'question'
                # check if answer
                elif (span_class == 'answer'):
                    current_p['call_section'] = 'answer'
                # default to presentation, in case of closing remarks for example
                else:
                    current_p['call_section'] = 'presentation'

                # no need to advance tracker as we were on text2 but found another speaker2, next section 
                # should again be text2
            
        else:
            # should never get here
            continue

    # append final p to call_dict
    call_dict['paragraphs'].append(current_p)

    return call_dict