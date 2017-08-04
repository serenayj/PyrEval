use strict;
use warnings;
use FindBin;

die "Usage: perl bin/Preprocess/change_format.pl model_dir is_train input_file output_file\n" if (@ARGV != 4);

my $home_dir = "$FindBin::Bin";
$home_dir =~ s/\/bin\/Preprocess$//;




my $input_dir = $ARGV[0];
#$input_dir = "../models/03-06";
my $tf = 1;
my $idf = 1;
my $norm = 0;

my $vocab_file = "$input_dir/vocab";
my $train_file = "$input_dir/train.clean";
#my $test_file = "$input_dir/test.mt";
my $idf_file = "$input_dir/idf";
my $is_train = $ARGV[1];
my $orig_file = $ARGV[2];
my $output_file = $ARGV[3];
print "is_train=$is_train\n";


my $file = $train_file;
$file = $orig_file if ($is_train == 0);

my $clean = 1;

### 1. remove infrequent words
my $cmd;
if ($is_train == 1) {
    $cmd = "perl $home_dir/bin/Preprocess/rm_infreq.pl $train_file $train_file.rmiw 2";
    print "$cmd\n";
    `$cmd`;
    #$train_file .= ".rmiw";
    $file .= ".rmiw";
    sleep(1);
}


### 2. index words
$cmd = "perl $home_dir/bin/Preprocess/index.pl $is_train $file $file.ind $vocab_file";
print "$cmd\n";
`$cmd`;
if ($clean == 1 && $is_train == 1) {
    $cmd = "rm $file";
    `$cmd`;
}
$file .= ".ind";
sleep(1);


### 3. tf idf weighting on words
$cmd = "perl $home_dir/bin/Preprocess/tfidf.pl $is_train $file $idf_file $tf $idf $norm";
print "$cmd\n";
`$cmd`;
if ($clean == 1) {
    $cmd = "rm $file";
    `$cmd`;
}
if ($tf == 1) {
    $file .= ".tf";
}
if ($idf == 1) {
    $file .= ".idf";
}
if ($norm == 1) {
    $file .= ".norm";
}
sleep(1);


### 6. convert into matlab format
$cmd = "perl $home_dir/bin/Preprocess/matlab_format.pl $file $file.ml";
#my $size = `wc -l $vocab_file`;
#$size =~ s/\s.*$//;
#$cmd = "perl $home_dir/bin/Preprocess/text_cpp_format.pl $file $file.ml $size";
print "$cmd\n";
`$cmd`;
if ($clean == 1) {
    $cmd = "rm $file";
    `$cmd`;
}
$file .= ".ml";

if ($file ne $output_file) {
    `mv $file $output_file`;
}
