use strict;
use warnings;
use FindBin;

### 0. initialize env variables
my $home_dir = "$FindBin::Bin";
$home_dir =~ s/\/bin$//;
#print "$home_dir\n";
if (defined $ENV{'PERL5LIB'}) {
    $ENV{'PERL5LIB'} = "$ENV{PERL5LIB}:$home_dir/lib/perl";
} else {
    $ENV{'PERL5LIB'} = "$home_dir/lib/perl";
}


my $clean = 1;
my $is_train = 1;

die "Usage:  perl  train.pl  model_dir  train_file  K  lambda  wm  alpha  n_itrs\n" if (@ARGV != 7);

my $model_dir = $ARGV[0];
my $train_file = $ARGV[1];
my $k = $ARGV[2];
my $lambda = $ARGV[3];
my $wm = $ARGV[4];
my $alpha = $ARGV[5];
my $n_itrs = $ARGV[6];



if ($train_file ne "$model_dir/train.txt") {
    `cp $train_file $model_dir/train.txt`;
}


### 1. preprocess text
my $cmd;
$cmd = "perl  $home_dir/bin/Preprocess/preprocess.pl  $model_dir/train.txt  $model_dir/train.clean";
print "[step 1]: $cmd\n\n";
`$cmd`;


### 2. change to matlab format
$cmd = "perl $home_dir/bin/Preprocess/change_format.pl  $model_dir  1  $model_dir/train.clean  $model_dir/train.ind";
print "[step 2]: $cmd\n\n";
`$cmd`;


### 3. apply ormf 
###$cmd = "nice matlab -nojvm -r \"path(path,'$home_dir/ormf'); train_ormf('$model_dir/train.ind', '$model_dir/model', $k, $lambda, $wm, $alpha, $n_itrs)\"";
$cmd = "matlab -nojvm -r \"path(path,'$home_dir/ormf'); train_ormf('$model_dir/train.ind', '$model_dir/model', $k, $lambda, $wm, $alpha, $n_itrs)\"";
print "[step 3]: $cmd\n\n";
print `$cmd`;

