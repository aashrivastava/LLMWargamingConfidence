import typing
import torch
from tqdm import tqdm
from selfcheckgpt.modeling_mqag import MQAG as mqag
from EvalsBase import EvaluatorBasics

class MQAGEval(EvaluatorBasics):
    '''
    Evaluates similarity of LLM generated texts using the automatic multiple-choice question answering framework. 
    Takes N sampled responses for a given query and calculates BERTScore between all combinations of pairs. Also aggregates these scores into one metric within 
    range [0, 1]. 
    '''
    def __init__(self, model: str='race', device: str='cuda'):
        print('Initializing MQAG Evaluator...')
        if device == 'cuda':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device('cpu')
        self.model = mqag(g1_model_type=model, device=self.device)
        super().__init__()

        print(f'MQAGScoreEval initialized to {self.device}')
    
    def create_pairs(self, responses: list[str], verbose: bool = False) -> list[tuple[str, str]]:
        '''
        Given a list of N responses, generate collection of possible pairs to use. There are N^2 pairs given I am including all permutations of pairs.

        Inputs:
            verbose: bool
                Indicates whether you want progress bar to show
        
        Outputs:
            List[Tuple[str, str]]: List (length N^2) of pairs
        '''
        pairs = [(response_i, response_j) for response_i in tqdm(responses, desc='Creating Pairs...', disable=not verbose) for response_j in responses]
        return pairs
    
    def score_questions(self, cand: str, ref: str, 
                        num_questions: int=3, scoring_method: str='counting', verbose: bool=False) -> int:
        '''
        IMPLEMENT DOCSTRING
        '''
        score = self.model.score(candidate=cand, reference=ref, num_questions=num_questions, verbose=verbose)
        score = score[scoring_method] # 0 is most alike, 1 is most unalike

        return score
    
    def aggregate(self, responses: list[str], num_questions: int=3, scoring_method: str='counting', verbose: bool=False) -> int:
        '''
        IMPLEMENT DOCSTRING
        '''
        N = len(responses)
        pairs = self.create_pairs(responses, verbose=verbose)
        tot = 0
        for t1, t2 in tqdm(pairs, desc='Calculating MQAGEval...', disable=not verbose):
            tot += self.score_questions(t1, t2, num_questions=num_questions, scoring_method=scoring_method, verbose=verbose)
        
        return tot / (N ** 2 - N)
    
if __name__ == '__main__':
    evaluator = MQAGScoreEval()
    ref = 'I think we should go to the store'
    contradict = 'I do not think we should go to the store'
    neutral = 'The mercedes is a good car'
    entails = 'I believe going to the store is a good idea'
    responses = [ref, entails, contradict, neutral]
    print(evaluator.aggregate(verbose=True))

        
        
