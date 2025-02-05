import pandas as pd
import argparse

def create_sample_dataset(input_csv, output_csv, sample_size=0.2, random_state=42):
    """
    원본 CSV 파일에서 샘플 데이터셋을 생성하는 함수.
    
    Args:
        input_csv (str): 원본 CSV 파일 경로
        output_csv (str): 생성될 샘플 CSV 파일 경로
        sample_size (float): 샘플 데이터 비율 (기본값: 0.2)
        random_state (int): 랜덤 시드 (기본값: 42)
    """
    # CSV 파일 로드
    df = pd.read_csv(input_csv)
    
    # 샘플 데이터 샘플링
    sample_df = df.sample(frac=sample_size, random_state=random_state)
    
    # 샘플 데이터 저장
    sample_df.to_csv(output_csv, index=False)
    print(f"샘플 데이터셋이 저장되었습니다: {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="샘플 데이터셋 생성")
    parser.add_argument("--input_csv", type=str, required=True, help="원본 CSV 파일 경로")
    parser.add_argument("--output_csv", type=str, required=True, help="저장할 샘플 CSV 파일 경로")
    parser.add_argument("--sample_size", type=float, default=0.2, help="샘플 데이터 비율 (기본값: 0.2)")
    parser.add_argument("--random_state", type=int, default=42, help="랜덤 시드 (기본값: 42)")
    
    args = parser.parse_args()
    create_sample_dataset(args.input_csv, args.output_csv, args.sample_size, args.random_state)
