# -*- coding: utf-8 -*-
"""
diamonds 데이터셋에 대한 EDA 스크립트

기능:
 - seaborn의 `diamonds` 데이터셋 로드
 - 기초 기술통계(여러 통계량) 생성
 - 6개 이상의 시각화 생성 및 이미지로 저장
 - 각 시각화 아래에 관련 기술통계를 교차표/피벗 형태로 출력
 - 모든 결과를 하나의 마크다운 파일로 저장

출력:
 - diamond/eda_report.md   (전체 리포트)
 - diamond/images/         (시각화 이미지 파일들)

주석과 설명은 모두 한국어로 작성되어 있습니다.
"""

from pathlib import Path
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def ensure_dirs(out_dir: Path):
    """출력 디렉터리를 생성합니다 (존재하지 않으면)."""
    out_dir.mkdir(parents=True, exist_ok=True)


def save_fig(fig, path: Path):
    """현재 figure를 파일로 저장하고 닫습니다.

    인자:
        fig: matplotlib figure 객체
        path: 저장할 파일 경로 (Path)
    """
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    """메인 처리 함수

    - 데이터 로드
    - 기초 통계 및 기술통계 생성
    - 시각화 생성 및 이미지 저장
    - 각 시각화에 대한 피벗/교차표 생성
    - 마크다운 리포트 작성
    """
    # 출력 경로 설정
    out_images = Path("diamond/images")
    out_report = Path("diamond/eda_report.md")
    ensure_dirs(out_images)

    # 데이터 로드 (seaborn 내장 데이터)
    df = sns.load_dataset("diamonds")

    # ---------------------------
    # 1) 기초 통계 계산
    # ---------------------------
    stats = {}
    stats['shape'] = df.shape
    stats['columns'] = list(df.columns)
    stats['missing_values'] = df.isna().sum()
    stats['describe'] = df.describe(include='all')
    stats['skew'] = df.skew(numeric_only=True)
    stats['kurtosis'] = df.kurtosis(numeric_only=True)
    stats['value_counts_cut'] = df['cut'].value_counts()
    stats['value_counts_color'] = df['color'].value_counts()
    stats['value_counts_clarity'] = df['clarity'].value_counts()
    stats['corr'] = df.select_dtypes(include=[np.number]).corr()

    # 마크다운 조각들을 모아서 한 번에 파일로 출력
    md_parts = []
    md_parts.append("# Diamonds EDA Report\n")
    md_parts.append("## 요약\n")
    md_parts.append(f"- 데이터셋 행/열: {stats['shape']}\n")
    md_parts.append(f"- 컬럼: {', '.join(stats['columns'])}\n")

    # 1) 기술통계: describe
    md_parts.append("## 기술 통계 (기초)\n")
    md_parts.append("### 요약 기술통계 (numeric)\n")
    try:
        md_parts.append(stats['describe'].to_markdown())
    except Exception:
        # to_markdown이 없을 경우 대비 (pandas 버전 차이)
        md_parts.append(stats['describe'].to_csv())

    # 왜도/첨도 추가
    md_parts.append("\n### Skewness\n")
    md_parts.append(stats['skew'].to_markdown())
    md_parts.append("\n### Kurtosis\n")
    md_parts.append(stats['kurtosis'].to_markdown())

    # 결측값 요약
    md_parts.append("\n### 결측값 검사\n")
    md_parts.append(stats['missing_values'].to_markdown())

    # 범주형 값 분포
    md_parts.append("\n### 범주형 분포\n")
    md_parts.append("**cut**\n")
    md_parts.append(stats['value_counts_cut'].to_markdown())
    md_parts.append("\n**color**\n")
    md_parts.append(stats['value_counts_color'].to_markdown())
    md_parts.append("\n**clarity**\n")
    md_parts.append(stats['value_counts_clarity'].to_markdown())

    # ---------------------------
    # 2) 시각화 및 관련 통계
    # ---------------------------
    md_parts.append("\n## 시각화 및 관련 기술통계\n")

    # 1) 가격 히스토그램
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(1, 1, 1)
    sns.histplot(df['price'], bins=50, kde=True, ax=ax)
    ax.set_title('Price Distribution')
    p1 = out_images / 'price_hist.png'
    save_fig(fig, p1)
    md_parts.append(f"### 1) Price 분포 (히스토그램)\n![price_hist]({p1.as_posix()})\n")
    # 히스토그램 관련 기술통계: 가격 구간별 개수
    price_bins = pd.cut(df['price'], bins=10)
    price_bins_table = df.groupby(price_bins)['price'].count().rename('count').to_frame()
    md_parts.append("#### 히스토그램 관련 집계(가격 구간별 개수)\n")
    md_parts.append(price_bins_table.to_markdown())

    # 2) Cut별 가격 박스플롯
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(1, 1, 1)
    sns.boxplot(x='cut', y='price', data=df, ax=ax)
    ax.set_title('Price by Cut (Boxplot)')
    p2 = out_images / 'price_by_cut_box.png'
    save_fig(fig, p2)
    md_parts.append(f"### 2) Cut별 Price 분포 (Boxplot)\n![price_by_cut_box]({p2.as_posix()})\n")
    cut_stats = df.groupby('cut')['price'].agg(['count', 'mean', 'median', 'std']).reset_index()
    md_parts.append("#### Cut별 기술통계\n")
    md_parts.append(cut_stats.to_markdown(index=False))

    # 3) 캐럿 vs 가격 산점도 (clarity로 색상 구분)
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)
    sns.scatterplot(x='carat', y='price', hue='clarity', data=df, palette='tab10', alpha=0.6, s=20, ax=ax)
    ax.set_title('Carat vs Price by Clarity')
    p3 = out_images / 'carat_price_scatter.png'
    save_fig(fig, p3)
    md_parts.append(f"### 3) Carat vs Price 산점도 (색깔: Clarity)\n![carat_price_scatter]({p3.as_posix()})\n")
    # carat 구간별 x clarity별 평균 가격 (피벗)
    df['carat_bin'] = pd.cut(df['carat'], bins=6)
    pivot1 = df.pivot_table(index='carat_bin', columns='clarity', values='price', aggfunc='mean')
    md_parts.append("#### Carat_bin x Clarity 평균 Price\n")
    md_parts.append(pivot1.round(2).to_markdown())

    # 4) Color별 Violin 플롯
    fig = plt.figure(figsize=(8, 5))
    ax = fig.add_subplot(1, 1, 1)
    sns.violinplot(x='color', y='price', data=df, inner='quartile', ax=ax)
    ax.set_title('Price by Color (Violin)')
    p4 = out_images / 'price_by_color_violin.png'
    save_fig(fig, p4)
    md_parts.append(f"### 4) Color별 Price 분포 (Violin)\n![price_by_color_violin]({p4.as_posix()})\n")
    color_stats = df.groupby('color')['price'].agg(['count', 'mean', 'median', 'std']).reset_index()
    md_parts.append("#### Color별 기술통계\n")
    md_parts.append(color_stats.to_markdown(index=False))

    # 5) 수치형 상관관계 히트맵
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_subplot(1, 1, 1)
    sns.heatmap(stats['corr'], annot=True, fmt='.2f', cmap='coolwarm', ax=ax)
    ax.set_title('Numeric Feature Correlation')
    p5 = out_images / 'corr_heatmap.png'
    save_fig(fig, p5)
    md_parts.append(f"### 5) 수치형 변수 상관관계 히트맵\n![corr_heatmap]({p5.as_posix()})\n")
    md_parts.append("#### 상관행렬(수치형)\n")
    md_parts.append(stats['corr'].round(3).to_markdown())

    # 6) Clarity 빈도 막대그래프
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_subplot(1, 1, 1)
    sns.countplot(x='clarity', data=df, order=df['clarity'].value_counts().index, ax=ax)
    ax.set_title('Clarity Counts')
    p6 = out_images / 'clarity_count.png'
    save_fig(fig, p6)
    md_parts.append(f"### 6) Clarity 빈도 (Countplot)\n![clarity_count]({p6.as_posix()})\n")
    clarity_cut_crosstab = pd.crosstab(df['clarity'], df['cut'])
    md_parts.append("#### Clarity x Cut 교차표\n")
    md_parts.append(clarity_cut_crosstab.to_markdown())

    # ---------------------------
    # 3) 리포트 파일로 저장
    # ---------------------------
    out_text = "\n\n".join(md_parts)
    out_report.write_text(out_text, encoding='utf-8')

    print(f"EDA 완료: 리포트 -> {out_report}, 이미지 폴더 -> {out_images}")


if __name__ == '__main__':
    main()
