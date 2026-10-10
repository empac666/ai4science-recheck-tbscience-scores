"""Frozen predictions: compared with outputs, never used as computed results."""
PREDICTIONS = {
    'AP-01': {'A':{'K':143,'N':210},'B':{'K':143,'N':210},'display':'68.1'},
    'AP-02': {'A':{'K':84,'N':210},'B':{'K':84,'N':210},'display':'40.0'},
    'AP-03': {'Astra':'3.2','Fable':'3.4','three_way_equal':True},
    'AP-04': {'Astra':True,'Fable':True},
    'AP-05': '一致', 'AP-06':'一致',
    **{f'AP-{i:02d}':'来源未完整披露' for i in range(7,12)},
    'AP-12':[133], 'AP-13':[46], 'AP-14':[138], 'AP-15':[24],
    'AP-16':[72], 'AP-17':[368], 'AP-18':[143], 'AP-19':[84],
}
ENUMERATION_SPEC = [
    ('AP-12','S1a',210,'same original document'),
    ('AP-13','S3',70,'assumed N; not written in announcement'),
    ('AP-14','S3',210,'assumed N; not written in announcement'),
    ('AP-15','S6',70,'assumed N; not written in announcement'),
    ('AP-16','S6',210,'assumed N; not written in announcement'),
    ('AP-17','S5',700,'same original document'),
    ('AP-18','S4',210,'same original document'),
    ('AP-19','S7',210,'same original document'),
]
